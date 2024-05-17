import os, requests, zipfile, io, json, time, copy, ssl, smtplib
import xml.etree.ElementTree as ET
from licitacion import Licitacion
from datetime import datetime, date
from variables import DATE_FORMAT, DATA_FOLDER
from enums import *
from email.message import EmailMessage
import connectionSQL
NAMESPACES = {'cbc': 'urn:dgpe:names:draft:codice:schema:xsd:CommonBasicComponents-2',
              'cac': 'urn:dgpe:names:draft:codice:schema:xsd:CommonAggregateComponents-2',
              'cac-place-ext':'urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonAggregateComponents-2',
              'cbc-place-ext': 'urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonBasicComponents-2'}

def remove_files(path):
    for file in os.listdir(path):
        os.remove(path + file)

def download_data(path, year, month):
    URL = f"https://contrataciondelsectorpublico.gob.es/sindicacion/sindicacion_643/licitacionesPerfilesContratanteCompleto3_{year}{month}.zip"
    r = requests.get(URL)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(path)

def convert_month(month: int):
    if month < 10:
        str_month = "0" + str(month)
    else:
        str_month = str(month)
    return str_month

def update():
    last_update = "" 
    mailing_list = []
    stack = []
    with open("config.json") as json_file:
        data = json.load(json_file)
        last_update = datetime.strptime(data['last_date_updated'],DATE_FORMAT)
    updated_month = last_update.month
    updated_year = last_update.year
    current_year = datetime.now().year
    current_month = datetime.now().month
    while(updated_year < current_year):
        while(updated_month < 13):
            download_data(DATA_FOLDER,updated_year, convert_month(updated_month))
            stack = create_file_stack(DATA_FOLDER, last_update)
            mailing_list.append(parse_stack(stack,DATA_FOLDER))
            remove_files(DATA_FOLDER)
            updated_month+=1
        updated_month = 1
        updated_year += 1
    while(current_month >= updated_month):
        download_data(DATA_FOLDER,updated_year, convert_month(updated_month))
        stack = create_file_stack(DATA_FOLDER, last_update)
        mailing_list.append(parse_stack(stack,DATA_FOLDER))
        remove_files(DATA_FOLDER)
        updated_month+=1
    return mailing_list

def extract_update_date(path: str):
    with open(path, "r") as file:
        for line in file:
            if "<updated>" in line:
                root = ET.fromstring(line)
                if root is not None:
                    return datetime.strptime(root.text.__str__(),DATE_FORMAT)

def get_name_next_file(path: str):
    with open(path, "r") as file:
        for i, line in enumerate(file):
            if "next" in line:
                root = ET.fromstring(line)
                actual_file = root.attrib.get('href')
                if actual_file and actual_file.find('/'):
                    actual_file = actual_file.split('/')[-1]
                return actual_file
            if i >= 100:
                return ""
    return ""


def create_file_stack(path, last_update):
    stack = []
    actual_file = "licitacionesPerfilesContratanteCompleto3.atom"
    file_update = extract_update_date(path+actual_file)
    next_file_exists = True
    while next_file_exists and file_update > last_update:
        file_update = extract_update_date(path + actual_file)
        stack.append((actual_file, file_update))
        actual_file = get_name_next_file(path+actual_file)
        if not os.path.exists(path+actual_file):
            next_file_exists = False
    return stack

def parse_stack(stack: list[tuple[str, datetime]], path):
    update_list = []
    while(stack):
        actual_file, file_update = stack.pop()
        times = []
        tree = ET.parse(path + actual_file)
        root = tree.getroot()
        print(f"el fichero es {actual_file} y la fecha de actualizacion es {file_update}")
        start = time.time()
        update_list.append(parse(root))
        end = time.time()
        print(end - start)
        time.sleep(10)
        times.append(end-start)
        with open("config.json", "r+") as json_file:
            data = json.load(json_file)
            data['last_date_updated'] = file_update.strftime(DATE_FORMAT)
            json_file.seek(0)
            json.dump(data, json_file)
            json_file.truncate()
    return update_list

def check_element(query: str, root: ET.Element):
    result = root.find(query)
    if result is not None:
        return result
    else:
        element = Element_mock("null")
        return element

def parse(root: ET.Element):
    update_list = []
    for entry in root.iter('{http://www.w3.org/2005/Atom}entry'):
        array = parse_entry(entry)
        if array is not None:
            for element in (array):
                if element is not None:
                    modified = connectionSQL.insert_licitacion(element)
                    if modified:
                        update_list.append(element)
    return update_list

def parse_lotes_en_plazo(procurementProject: ET.Element, numero_de_lote: int, licitacion: Licitacion):
    lote = copy.deepcopy(licitacion)
    objeto_de_lote = procurementProject.find('cbc:Name')
    if objeto_de_lote is not None:
        lote.Objeto_licitacion_lote = objeto_de_lote.text.__str__()
    budget_section = procurementProject.find('cac:BudgetAmount')
    if budget_section is None:
        print("budget")
        return
    presupuesto_base = budget_section.find('cbc:TaxExclusiveAmount')
    if presupuesto_base is not None:
        lote.Presupuesto_base_sin_impuestos_licitacion_lote = presupuesto_base.text.__str__()
    lote.Id_de_lote = str(numero_de_lote+1)
    return lote


def parse_lotes_terminados(tenderResult: ET.Element, procurementProject: ET.Element, numero_de_lote: int, licitacion: Licitacion):
    lote = copy.deepcopy(licitacion)
    objeto_de_lote = procurementProject.find('cbc:Name')
    if objeto_de_lote is not None:
        lote.Objeto_licitacion_lote = objeto_de_lote.text.__str__()
    budget_section = procurementProject.find('cac:BudgetAmount')
    if budget_section is None:
        print("budget")
        return
    presupuesto_base = budget_section.find('cbc:TaxExclusiveAmount')
    if presupuesto_base is not None:
        lote.Presupuesto_base_sin_impuestos_licitacion_lote = presupuesto_base.text.__str__()
    resultCode = tenderResult.find('cbc:ResultCode')
    if resultCode is not None:
        lote.Resultado_licitacion_lote = resultados_de_procedimiento.get(resultCode.text.__str__(),"null")
    tender_quantity = tenderResult.find('cbc:ReceivedTenderQuantity')
    if tender_quantity is not None and tender_quantity.text is not None:
        lote.Numero_de_ofertas_recibidas_por_licitacion_lote = tender_quantity.text
    if lote.Resultado_licitacion_lote == "Formalizado" or lote.Resultado_licitacion_lote == "Resuelta":
        contract_section = tenderResult.find('cac:WinningParty')
        if contract_section is None:
            print('2')
            exit(1)
        contract_section = contract_section.find('cac:PartyName')
        if contract_section is None:
            print('3')
            exit(1)
        contracter = contract_section.find('cbc:Name')
        if contracter is not None:
            lote.Adjudicatario_licitacion_lote = contracter.text.__str__()
        payable_section = tenderResult.find('cac:AwardedTenderedProject')
        if payable_section is None:
            print('4')
            exit(1)
        payable_section = payable_section.find('cac:LegalMonetaryTotal')
        if payable_section is None:
            print('5')
            exit(1)
        payable_amount = payable_section.find('cbc:PayableAmount')
        if payable_amount is not None:
            lote.Importe_adjudicacion_sin_impuestos_licitacion_lote = payable_amount.text.__str__()
    lote.Id_de_lote = str(numero_de_lote + 1)
    return lote



def parse_entry(root: ET.Element):
    licitacion = Licitacion()
    id = root.find('{http://www.w3.org/2005/Atom}id')
    licitacion.Identificador = id.text.split('/')[-1] if id is not None and id.text is not None else "error al parsear"
    link = root.find('{http://www.w3.org/2005/Atom}link')
    licitacion.Link_licitacion = link.attrib['href'] if link is not None else "error al parsear"
    updated = root.find('{http://www.w3.org/2005/Atom}updated')
    licitacion.Fecha_actualizacion = updated.text if updated is not None and updated.text is not None else ""
    entry = root.find('cac-place-ext:ContractFolderStatus')
    if entry is None:
        return
    licitacion.Numero_expediente = check_element('cbc:ContractFolderID', entry).text.__str__()
    licitacion.Estado = codigos_de_estado.get(check_element('cbc-place-ext:ContractFolderStatusCode', entry).text.__str__(),"null")
    procurementProject = entry.find('cac:ProcurementProject')
    if procurementProject is None:
        print("procPorject")
        return
    licitacion.Tipo_de_contrato = tipos_de_contrato.get(check_element('cbc:TypeCode',procurementProject).text.__str__(), "null")
    licitacion.Objeto_del_Contrato = check_element('cbc:Name',procurementProject).text.__str__()
    budget_section = procurementProject.find('cac:BudgetAmount')
    if budget_section is None:
        print("budget")
        return
    licitacion.Presupuesto_base_sin_impuestos = check_element('cbc:TaxExclusiveAmount',budget_section).text.__str__()
    for cpv_section in procurementProject.iter('cac:RequiredCommodityClassification'):
        if cpv_section is None:
            print("cpv2")
            return
        licitacion.Cpv.append(check_element('cbc:ItemClassificationCode',cpv_section).text.__str__())
    location_section = procurementProject.find('cac:RealizedLocation')
    if location_section is None:
        print("location")
        return
    licitacion.Lugar_de_ejecucion = check_element('cbc:CountrySubentityCode', location_section).text.__str__() + " - " + check_element('cbc:CountrySubentity',location_section).text.__str__()
    contratador_section = entry.find('cac-place-ext:LocatedContractingParty')
    if contratador_section is None:
        print('contratador')
        return
    contratador_section = contratador_section.find('cac:Party')
    if contratador_section is None:
        print('contratador2')
        return 
    contratador_section = contratador_section.find('cac:PartyName')
    if contratador_section is None:
        print('contractor3')
        return
    licitacion.Organo_de_Contratacion = check_element('cbc:Name', contratador_section).text.__str__()
    tenderingProcess = entry.find('cac:TenderingProcess')
    if tenderingProcess is None:
        print('tendering process')
        return 
    licitacion.Tipo_de_procedimiento = tipos_de_procedimiento.get(check_element('cbc:ProcedureCode', tenderingProcess).text.__str__(), "no asignado")
    licitacion.Sistema_de_contratacion = sistemas_de_contratacion.get(check_element('cbc:ContractingSystemCode', tenderingProcess).text.__str__(),"null")
    fecha_de_presentacion_de_ofertas = tenderingProcess.find('cac:TenderSubmissionDeadlinePeriod')
    if fecha_de_presentacion_de_ofertas is None:
        print('fecha de presentacion de ofertas')
        # print(licitacion)
        return 
    hora_de_presentacion_de_ofertas = fecha_de_presentacion_de_ofertas.find('cbc:EndTime')
    fecha_de_presentacion_de_ofertas = fecha_de_presentacion_de_ofertas.find('cbc:EndDate')
    if hora_de_presentacion_de_ofertas is not None and fecha_de_presentacion_de_ofertas is not None:
        licitacion.Fecha_de_presentacion_de_ofertas = fecha_de_presentacion_de_ofertas.text.__str__() + " " + hora_de_presentacion_de_ofertas.text.__str__()
    minimum = '9999-01-01'
    for notices in entry.iter('cac-place-ext:ValidNoticeInfo'):
        notice_section = notices.find('cac-place-ext:AdditionalPublicationStatus')
        if notice_section is None:
            print('notice section')
            return
        notice_section = notice_section.find('cac-place-ext:AdditionalPublicationDocumentReference')
        if notice_section is None:
            print('notice section 2')
            return
        notice = notice_section.find('cbc:IssueDate')
        if notice is not None:
            notice_date = notice.text
            if notice_date is not None and notice_date < minimum:
                minimum = notice_date
    licitacion.Primera_publicacion = minimum
    numero_de_lotes = 0
    for _ in entry.iter('cac:ProcurementProjectLot'):
        numero_de_lotes+=1
    procurement_project_lot = entry.findall('cac:ProcurementProjectLot')
    tender_results = entry.findall('cac:TenderResult')
    array_lotes = []
    if numero_de_lotes == 0:
        if licitacion.Estado != "En plazo" and licitacion.Estado != "Evaluada" and licitacion.Estado != "Anulada" and len(tender_results)==1:
            array_lotes.append(parse_lotes_terminados(tender_results[0], procurementProject, 0, licitacion))
        else:
            array_lotes.append(parse_lotes_en_plazo(procurementProject, 0, licitacion))
    for i in range(0,numero_de_lotes):
        procurementProject = procurement_project_lot[i].find('cac:ProcurementProject')
        if procurementProject is not None:
            if licitacion.Estado != "En plazo" and licitacion.Estado != "Evaluada" and licitacion.Estado != "Anulada" and i < len(tender_results):
                array_lotes.append(parse_lotes_terminados(tender_results[i], procurementProject, i, licitacion))
            else:
                array_lotes.append(parse_lotes_en_plazo(procurementProject, i, licitacion))
    return array_lotes

def send_mail(licitaciones: list[Licitacion]):
    emails = []
    email_sender = "licitacionestfgupm@gmail.com"
    email_pass = "xevs qyli kpqt hkhq"
    with open("config.json") as file:
        data = json.load(file)
        emails = data["emails"]
    subject = f"Licitaciones actualizadas el {date.today()}"
    body = ""
    for licitacion in licitaciones:
        body += licitacion.__str__()
        print(licitacion)
        body += "\n"
    em = EmailMessage()
    em['From'] = email_sender
    em['Subject'] = subject
    em.set_content(body)
    for receiver in emails:
        em['To'] = receiver
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_pass)
            smtp.sendmail(email_sender, receiver,em.as_string())

if __name__ == "__main__":
    licitaciones = update()
    if licitaciones:
        send_mail(licitaciones)
