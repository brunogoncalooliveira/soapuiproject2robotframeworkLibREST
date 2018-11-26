import untangle
import os
import argparse
from pprint import pprint

def get_variables(resource):
    arr = resource.split('{')
    vars = []
    for i in arr:
        if '}' in i:
            var = i.split('}')[0]
            vars.append(var)
    return vars

def get_headers_seguranca(cdata):
    arr = {}
    #txt = ''
    a = cdata.split("key=\"")[1:]
    for k in a:
        t = k.split("\" value=\"")
        nome = t[0]
        valor = t[1].split("\"")[0]
        arr[nome] = valor
    return arr


def get_info(apiname, con_method, name):
    res = {}
    methodname = apiname.strip('.') + ' - ' + con_method['name']

    headers = {}

    res['method'] = con_method['method']
    res['resource'] = name
    res['documentation'] = con_method.con_description.cdata.replace("\n", '|')
    res['endpoint'] = con_method.con_request.con_endpoint.cdata
    headers = get_headers_seguranca(con_method.con_request.con_settings.con_setting.cdata)
    #pprint(res['seguranca'])
    for header in con_method.con_request.con_parameters.con_entry:
        headers[header['key']] = header['value']
    res['headers'] = headers
    res['body'] = con_method.con_request.con_request.cdata.replace("\n", '')

    return {'method': methodname, 'data': res}

def get_record_with_more_occurences(arr):
    tarr = {}

    for i in arr:
        if i not in tarr:
            tarr[i] = 1
        else:
            tarr[i] += 1

    max = 0
    for i in tarr:
        if tarr[i] > max:
            max = tarr[i]

    for i in tarr:
        if tarr[i] == max:
            if i == '':
                return '\\'
            else:
                return i

    return '\\'

def gerar_robot(methods):
    txt = "*** Settings ***\n"

    #
    # construir Library
    #
    um_endpoint = False
    endpoint = []
    for i in methods:
        if methods[i]['endpoint'] not in endpoint:
            endpoint.append(methods[i]['endpoint'])

    if len(endpoint) == 1:
        um_endpoint = True

    if um_endpoint:
        txt += "Library       REST    {}  ssl_verify=false\n\n".format(endpoint[0])

    #
    # construir Default Variables
    #
    txt += "*** Variables ***\n\n"

    headers = {}
    for i in methods:
        tmethod = methods[i]['headers']
        for h in tmethod:
            if h not in headers:
                headers[h] = [tmethod[h]]
            else:
                headers[h].append(tmethod[h])

    max = 0
    for i in headers:

        tlen = len('${default-' + i + '}')
        #print(tlen)
        if tlen > max:
            max = tlen
    max += 2

    for i in headers:
        txt += ('${default-' + i + '}').ljust(max) + get_record_with_more_occurences(headers[i]) + "\n"
        #txt += i + ' - ' + get_record_with_more_occurences(headers[i]))

    #
    # construir Default Variables
    #
    txt += "\n\n*** Keywords ***\n\n"

    for i in methods:
        #pprint(methods[i])
        #exit()
        txt += "\n\n" + i +"\n"
        first = True
        body = ''
        for h in methods[i]['headers']:
            if first:
                txt += "  [Arguments]  ${" + h + "}=${default-" + h + "}\n"
                first = False
            else:
                txt += "  ...          ${" + h + "}=${default-" + h + "}\n"
        if methods[i]['body'] != '':
            body = methods[i]['body']
            while "\t" in body:
                body = body.replace('\t','')
            while '{  ' in body:
                body = body.replace('{  ', '{ ')
            while '  }' in body:
                body = body.replace('  }', ' }')
            while ',  ' in body:
                body = body.replace(',  ', ', ')

            txt += "  ...          ${body}=" + body + "\n"


        for h in methods[i]['headers']:
            txt += "  Set Headers  { \"" + h + "\": \"${" + h + "}\"}\n"

        if body != '':
            txt += "  " + methods[i]['method'] + '  ' + methods[i]['resource'].replace('{', '${') + '  ${body}'
        else:
            txt += "  " + methods[i]['method'] + '  ' + methods[i]['resource'].replace('{', '${')

    return txt

def main(inputfile, outputfile):
    arr ={}
    soapaui_project = inputfile
    interfaces = untangle.parse(soapaui_project)

    for i in interfaces.con_soapui_project.con_interface:
        apiname = i['name']
        if type(i.con_resource) is list:
            # quando só existe mais que 1 resource
            for resource in i.con_resource:
                if type(resource.con_method) is list:
                    for cmethod in resource.con_method:
                        data = get_info(apiname, cmethod, resource['name'])
                        arr[data['method']] = data['data']
                else:
                    data = get_info(apiname, resource.con_method, resource['name'])
                    arr[data['method']] = data['data']
        else:
            # quando só existe 1 resource
            data = get_info(apiname, i.con_resource.con_method, i.con_resource['name'])
            arr[data['method']] = data['data']
    txt = gerar_robot(arr)

    fo = open(outputfile, 'w')
    fo.write(txt)
    fo.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Este script cria um ficheiro em formato robot framework, com a invocação de métodos de uma API REST a partir de um projecto em SOAPUI"
    )

    parser.add_argument('inputfile', help="nome do ficheiro de input")
    parser.add_argument('outputfile', help="nome do ficheiro de output (normalmente com extensão .robot)")

    # Parse the arguments
    arguments = parser.parse_args()
    print(arguments.inputfile)
    print(arguments.outputfile)
    main(arguments.inputfile, arguments.outputfile)
