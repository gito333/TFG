import os, requests, zipfile, io, json, copy, ssl, smtplib, itertools
import xml.etree.ElementTree as ET
from licitacion import Licitacion
from datetime import datetime, date
from variables import DATE_FORMAT, DATA_FOLDER ,CONFIG_LOCATION, URLS, NAMESPACES
from utils import get_cpv
from enums import *
from email.message import EmailMessage
import dbconnection as dbconnection

def remove_files(path):
    for file in os.listdir(path):
        os.remove(path + file)

def download_data(path, year, month, url):
    URL = f"{url}{year}{month}.zip"
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
    with open(f"{CONFIG_LOCATION}config.json") as json_file:
        data = json.load(json_file)
        last_update = datetime.strptime(data['last_date_updated'],DATE_FORMAT)
    updated_month = last_update.month
    updated_year = last_update.year
    current_year = datetime.now().year
    current_month = datetime.now().month
    for url in URLS:
        while(updated_year < current_year):
            while(updated_month < 13):
                download_data(DATA_FOLDER,updated_year, convert_month(updated_month), url[0])
                stack = create_file_stack(DATA_FOLDER, last_update, url[1])
                mailing_list.append(parse_stack(stack,DATA_FOLDER))
                remove_files(DATA_FOLDER)
                updated_month+=1
            updated_month = 1
            updated_year += 1
        while(current_month >= updated_month):
            download_data(DATA_FOLDER,updated_year, convert_month(updated_month), url[0])
            stack = create_file_stack(DATA_FOLDER, last_update, url[1])
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


def create_file_stack(path, last_update, actual_file):
    stack = []
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
        # times = []
        tree = ET.parse(path + actual_file)
        root = tree.getroot()
        print(f"el fichero es {actual_file} y la fecha de actualizacion es {file_update}")
        # start = time.time()
        update_list.append(parse(root))
        # end = time.time()
        # print(end - start)
        # time.sleep(10)
        # times.append(end-start)
        with open(f"{CONFIG_LOCATION}config.json", "r+") as json_file:
            data = json.load(json_file)
            data['last_date_updated'] = file_update.strftime(DATE_FORMAT)
            json_file.seek(0)
            json.dump(data, json_file)
            json_file.truncate()
    return update_list

def check_element(query: str, root: ET.Element):
    result = root.find(query, NAMESPACES)
    if result is not None:
        return result
    else:
        element = Element_mock("null")
        return element

def parse(root: ET.Element):
    update_list = []
    for entry in root.iter('{http://www.w3.org/2005/Atom}entry'):
        # start = time.time()
        array = parse_entry(entry)
        if array is not None:
            for element in array:
                if element is not None:
                    modified = dbconnection.insert_licitacion(element)
                    if modified:
                        update_list.append(element)
        # end = time.time()
        # print(end-start)
    return update_list

def parse_entry(root: ET.Element):
    licitacion = Licitacion()
    id = root.find('{http://www.w3.org/2005/Atom}id')
    licitacion.Identificador = id.text.split('/')[-1] if id is not None and id.text is not None else "error al parsear"
    link = root.find('{http://www.w3.org/2005/Atom}link')
    licitacion.Link_licitacion = link.attrib['href'] if link is not None else "error al parsear"
    updated = root.find('{http://www.w3.org/2005/Atom}updated')
    licitacion.Fecha_actualizacion = updated.text if updated is not None and updated.text is not None else ""
    entry = root.find('cac-place-ext:ContractFolderStatus', NAMESPACES)
    if entry is None:
        return
    licitacion.Numero_expediente = check_element('cbc:ContractFolderID', entry).text.__str__()
    licitacion.Estado = codigos_de_estado.get(check_element('cbc-place-ext:ContractFolderStatusCode', entry).text.__str__(),"null")
    contratador_section = entry.find('cac-place-ext:LocatedContractingParty',NAMESPACES)
    if contratador_section is not None:
        contratador_section = contratador_section.find('cac:Party',NAMESPACES)
        if contratador_section is not None:
            contratador_section = contratador_section.find('cac:PartyName',NAMESPACES)
            if contratador_section is not None:
                licitacion.Organo_de_Contratacion = check_element('cbc:Name', contratador_section).text.__str__()
    procurementProject = entry.find('cac:ProcurementProject', NAMESPACES)
    if procurementProject is not None:
        licitacion.Tipo_de_contrato = tipos_de_contrato.get(check_element('cbc:TypeCode',procurementProject).text.__str__(), "null")
        # existe subtipo de contrato para obras y servicios
        licitacion.Objeto_del_Contrato = check_element('cbc:Name',procurementProject).text.__str__()
        budget_section = procurementProject.find('cac:BudgetAmount',NAMESPACES)
        if budget_section is not None:
            licitacion.Presupuesto_base_sin_impuestos = check_element('cbc:TaxExclusiveAmount',budget_section).text.__str__()
        cpv_sections = procurementProject.findall('cac:RequiredCommodityClassification',NAMESPACES)
        for cpv_section in cpv_sections:
            licitacion.Cpv.append(check_element('cbc:ItemClassificationCode',cpv_section).text.__str__())
        location_section = procurementProject.find('cac:RealizedLocation',NAMESPACES)
        if location_section is not None:
            licitacion.Lugar_de_ejecucion = check_element('cbc:CountrySubentityCode', location_section).text.__str__() + " - " + check_element('cbc:CountrySubentity',location_section).text.__str__()
    tenderingProcess = entry.find('cac:TenderingProcess',NAMESPACES)
    if tenderingProcess is not None:
        licitacion.Tipo_de_procedimiento = tipos_de_procedimiento.get(check_element('cbc:ProcedureCode', tenderingProcess).text.__str__(), "no asignado")
        licitacion.Sistema_de_contratacion = sistemas_de_contratacion.get(check_element('cbc:ContractingSystemCode', tenderingProcess).text.__str__(),"null")
        # existe un tipo de urgencia en tramitacion
        fecha_de_presentacion_de_ofertas = tenderingProcess.find('cac:TenderSubmissionDeadlinePeriod',NAMESPACES)
        if fecha_de_presentacion_de_ofertas is not None:
            hora_de_presentacion_de_ofertas = fecha_de_presentacion_de_ofertas.find('cbc:EndTime',NAMESPACES)
            fecha_de_presentacion_de_ofertas = fecha_de_presentacion_de_ofertas.find('cbc:EndDate',NAMESPACES)
            if hora_de_presentacion_de_ofertas is not None and fecha_de_presentacion_de_ofertas is not None:
                licitacion.Fecha_de_presentacion_de_ofertas = fecha_de_presentacion_de_ofertas.text.__str__() + " " + hora_de_presentacion_de_ofertas.text.__str__()
            else:
                descripcion = tenderingProcess.find('cbc:Description', NAMESPACES)
                licitacion.Fecha_de_presentacion_de_ofertas = descripcion.text if descripcion is not None and descripcion.text is not None else ""
    minimum = '9999-01-01'
    notices = entry.findall('cac-place-ext:ValidNoticeInfo',NAMESPACES)
    for notice in notices:
        publication_status = notice.findall('cac-place-ext:AdditionalPublicationStatus',NAMESPACES)
        for publication in publication_status:
            mediums = publication.findall('cac-place-ext:AdditionalPublicationDocumentReference',NAMESPACES)
            for medium in mediums:
                notice_date = medium.find('cbc:IssueDate',NAMESPACES)
                if notice_date is not None and notice_date.text is not None and notice_date.text < minimum:
                    minimum = notice_date.text
    licitacion.Primera_publicacion = minimum
    procurement_project_lots = entry.findall('cac:ProcurementProjectLot',NAMESPACES)
    tender_results = entry.findall('cac:TenderResult',NAMESPACES)
    licitacion.Id_de_lote = "0"
    array_lotes = []
    array_lotes.append(licitacion)
    for i,procurement_project_lot in enumerate(procurement_project_lots):
        array_lotes.append(eval_proc_project(licitacion, procurement_project_lot, i+1))
    for tender_result in tender_results:
        eval_tender_results(array_lotes, tender_result)
    return array_lotes

def eval_proc_project(licitacion: Licitacion, root: ET.Element, ids):
    lote = copy.deepcopy(licitacion)
    id = root.find('cbc:ID', NAMESPACES)
    lote.Id_de_lote = id.text.__str__() if id is not None else str(ids)
    proc = root.find('cac:ProcurementProject',NAMESPACES)
    if proc is not None:
        objeto_de_lote = proc.find('cbc:Name',NAMESPACES)
        if objeto_de_lote is not None:
            lote.Objeto_licitacion_lote = objeto_de_lote.text.__str__()
        budget_section = proc.find('cac:BudgetAmount',NAMESPACES)
        if budget_section is not None:
            presupuesto_base = budget_section.find('cbc:TaxExclusiveAmount',NAMESPACES)
            if presupuesto_base is not None:
                lote.Presupuesto_base_sin_impuestos_licitacion_lote = presupuesto_base.text.__str__()
    return lote

def eval_tender_results(array_lotes: list[Licitacion], root: ET.Element):
    awarded_tender = root.find('cac:AwardedTenderedProject',NAMESPACES)
    if awarded_tender is not None:
        id = awarded_tender.find('cbc:ProcurementProjectLotID',NAMESPACES)
        id = id.text if id is not None else None
        lote = 0
        if id is None:
            id = "0"
        for l in array_lotes:
            if l.Id_de_lote == id.__str__():
                lote = l
        if lote == 0:
            pass
        else:
            # si no encontramos awarded_tender no podemos saber que posicion del array es
            presupuesto = awarded_tender.find('cac:LegalMonetaryTotal',NAMESPACES)
            if presupuesto is not None:
                payable_amount = presupuesto.find('cbc:PayableAmount',NAMESPACES)
                lote.Importe_adjudicacion_sin_impuestos_licitacion_lote = payable_amount.text.__str__() if payable_amount is not None else "error en la facturación"
            resultCode = root.find('cbc:ResultCode',NAMESPACES)
            if resultCode is not None:
                lote.Resultado_licitacion_lote = resultados_de_procedimiento.get(resultCode.text.__str__(),"null")
            tender_quantity = root.find('cbc:ReceivedTenderQuantity',NAMESPACES)
            lote.Numero_de_ofertas_recibidas_por_licitacion_lote = tender_quantity.text.__str__() if tender_quantity is not None else "error en numero de ofertas recibidas"
            contract_section = root.find('cac:WinningParty',NAMESPACES)
            if contract_section is not None:
                contract_section = contract_section.find('cac:PartyName',NAMESPACES)
                if contract_section is not None:
                    contracter = contract_section.find('cbc:Name',NAMESPACES)
                    if contracter is not None:
                        lote.Adjudicatario_licitacion_lote = contracter.text.__str__()



def send_mail(licitaciones: list[Licitacion]):
    emails = []
    email_sender = "licitacionestfgupm@gmail.com"
    email_pass = "xevs qyli kpqt hkhq"
    with open(f"{CONFIG_LOCATION}config.json") as file:
        data = json.load(file)
        emails = data["emails"]
    subject = f"Licitaciones actualizadas el {date.today()}"
    body = ""
    for licitacion in licitaciones:
        body += str(licitacion)
        body += "\n"
    for receiver in emails:
        em = EmailMessage()
        em['From'] = email_sender
        em['Subject'] = subject
        em.set_content(body)
        em['To'] = receiver
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_pass)
            try:
                smtp.sendmail(email_sender, receiver,em.as_string())
            except Exception as e:
                smtp.sendmail(email_sender, receiver, str(e))

if __name__ == "__main__":
    if not os.path.exists(f'{CONFIG_LOCATION}config.json'):
        print("No existe el archivo de configuración")
        exit(-1)
    get_cpv()
    array_licitaciones = update()[0]
    licitaciones = list(itertools.chain.from_iterable(array_licitaciones))
    for i in range(0, len(licitaciones), 130):
        if licitaciones:
            send_mail(licitaciones[i:(min(len(licitaciones)-i,i+130-i) + i)])
