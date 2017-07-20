#!
# coding=utf-8
# dir_path = os.path.dirname(os.path.realpath(__file__))
#
from __future__ import print_function
from __future__ import print_function

import copy
import json

import flask
import requests

# import flask.ext
#
from client import app
from client import db

#
db.connect()  # the connection spends 1.8s
purpose = "goi database test_sending"
dataForQuery = {'selector': {"_id": {"$gt": 0}}, 'fields': ["_id", "_rev", "sensor_light", "sensor_temperature"],
                'sort': [{"_id": "asc"}]}


def checkNameQueryIndexes(query_indexes, name):
    """

    :param query_indexes:
    :param name:
    :return:
    """
    for x in range(0, query_indexes['total_rows']):
        if query_indexes['indexes'][x]['name'] == name:
            return True
    return False


def getDataFolowTime(name_database, fields):
    """

    :param name_database:
    :param fields:
    :return:
    """
    json_query = {"selector": {"rightNow": {"$gt": 0}}, "fields": fields, "sort": [{"rightNow": "desc"}]}
    if not str(name_database) in db.all_dbs():
        db.create_database(name_database)
    else:
        # print "This Database exists!\n"
        database_test_send = db[name_database]
        query_indexes = database_test_send.get_query_indexes(raw_result=True)
        # #print query_indexes
        # Create query index about TIME
        if not checkNameQueryIndexes(query_indexes, "time"):
            database_test_send.create_query_index(design_document_id="_design/time", index_name="rightNow",
                                                  index_type="json", fields=[{"rightNow": "desc"}])
        docs = database_test_send.get_query_result(json_query['selector'], json_query['fields'],
                                                   sort=json_query['sort'], raw_result=True)

        # data=[]
        # for doc in docs['docs']:
        # data.append(doc)
        return docs
    return {}


@app.route('/api/getdatajson/<namedatabase>', methods=['GET', 'POST'])
def getdatajson(namedatabase):
    """

    :param namedatabase:
    :return:
    """
    sensor_field = "payload"
    fields = ["_id", "rightNow", "type", sensor_field]
    dataraw = getDataFolowTime(namedatabase, fields)['docs']
    # data = {}

    # for Sensor in dataraw[0]['payload'][Node].keys():
    #     data[Node].update({Sensor:{"value":[], "labels":[]}})
    #     for x in xrange(0,len(dataraw)):
    #         if (Node in dataraw[x]['payload']) and (Sensor in dataraw[x]['payload'][Node]):
    #             data[Node][Sensor]["labels"].append(dataraw[x]['rightNow'])
    #             data[Node][Sensor]["value"].append(dataraw[x]['payload'][Node][Sensor])
    #     else: return "Error"
    return flask.jsonify(results=dataraw)


# return data for Seasons Page
@app.route('/api/getalldata/<namedatabase>', methods=['GET', 'POST'])
def get_alldata(namedatabase):
    """

    :param namedatabase:
    :return:
    """
    json_value = {"value": [], }
    fields = ["_id", "rightNow", "payload"]
    dataraw = getDataFolowTime(namedatabase, fields)

    if dataraw is {}:
        return "Error"
    dataraw = dataraw["docs"]
    # return flask.jsonify(results=dataraw)
    # Create the Shell Data for reponse POST methods
    sampledata = requests.get(str(flask.request.url_root) + "api/newsampledata/" + str(namedatabase))
    sampledata = json.loads(sampledata.text)

    if 'results' in sampledata:
        data = copy.deepcopy(sampledata["results"])
        if data == 'Error':
            return flask.jsonify(results="Error")

        for node in data.keys():
            for sensorName in data[node]['payload'].keys():
                data[node]['payload'][sensorName]['payload'] = copy.deepcopy(json_value)
                data[node]['time'] = []
                for x in range(0, len(dataraw)):
                    if node in dataraw[x]['payload'].keys():
                        data[node]['payload'][sensorName].pop('value', None)
                        data[node]['time'].append(dataraw[x]['rightNow'])
                        if sensorName in dataraw[x]['payload'][node]['payload'].keys():
                            data[node]['payload'][sensorName]['payload']["value"].append(
                                dataraw[x]['payload'][node]['payload'][sensorName]['value'])
                        else:
                            data[node]['payload'][sensorName]['payload']["value"].append(0)
        return flask.jsonify(results=data)
    return flask.jsonify(results="Error")


# @app.route('/api/savefilecsv/<namedatabase>')
# def save_file_from_CloudantDB(namedatabase):
#     fields = ["_id","rightNow","payload"]
#     # dataraw=get_data_folowTime(namedatabase,fields)
#     # docs = requests.get(str(request.url_root) + "api/getalldata/"+str(namedatabase))
#     # return jsonify(results=docs.text)
#     output = flask.ext.excel.make_response_from_array(datacsv, 'csv')
#     output.headers["Content-Disposition"] = "attachment; filename=export.csv"
#     output.headers["Content-type"] = "text/csv"
#     return output


@app.route('/api/importjsonfile/<namefile>')
def importjsonfile(namefile):
    # data=get_data('test_sending')
    """

    :param namefile:
    :return:
    """
    name = namefile + '.json'
    with open(name) as json_data:
        data = json.load(json_data)
        return flask.jsonify(results=data)


@app.route('/api/createanewseason', methods=['GET', 'POST'])
def create_a_new_season():
    """

    :return:
    """
    name = str(flask.request.form["name"])
    # tree = str(flask.request.form["tree"])
    # doc = db['design_seasons'].get_design_document("design_seasons")

    # Create infomation of seasons in design_seasons database
    numerical = 1
    name_new_season = "s_" + str(numerical)
    #
    while name_new_season in db.all_dbs():
        numerical += 1
        name_new_season = "s_" + str(numerical)
    #
    jsonstr = {"nameWeb": name, "nameSeason": name_new_season, "numerical": numerical}
    design_document = db['design_seasons']['_design/design_seasons']
    design_document['seasons'].append(jsonstr)
    print((design_document['seasons']))
    design_document.save()
    db.db_updates()
    # Create a new database
    db.create_database(name_new_season)
    # del docsample
    return flask.render_template("success.html")


@app.route('/api/deleteseason', methods=['GET', 'POST'])
def deleteseason():
    """
    :return:
    """
    if flask.request.method == 'POST':
        numerical = int(flask.request.form['selectDelete'])
        docsample = copy.deepcopy(db['design_seasons'].get_design_document('design_seasons'))
        design_document = db['design_seasons']['_design/design_seasons']
        del design_document['seasons'][numerical]
        design_document.save()
        return flask.render_template("success.html")
        return "OK"
    return "Error"


@app.route('/api/getseasons', methods=['GET', 'POST'])
def getseasons():
    """

    :return:
    """
    doc = db['design_seasons'].get_design_document('design_seasons')
    array_seasons = copy.deepcopy(doc['seasons'])
    if not array_seasons:
        return flask.jsonify(results={})
    jsonstr = copy.deepcopy(array_seasons[0])
    for key in jsonstr.keys():
        jsonstr[key] = []
    if array_seasons is not []:
        for season in array_seasons:
            for key in jsonstr.keys():
                jsonstr[key].append(season[key])
    return flask.jsonify(results=jsonstr)


# return the Sample Data when Devices is change.
# Example : Add/remove Node or Sensor in Device
@app.route("/api/newsampledata/<namedatabase>", methods=['GET', 'POST'])
def newsampledata(namedatabase):
    """

    :param namedatabase:
    :return:
    """
    if '_design/newsampledata' in db[namedatabase].list_design_documents():
        docs = db[namedatabase].get_design_document("_design/newsampledata")
        # print docs.keys()
        if 'payload' in docs.keys():
            return flask.jsonify(results=docs['payload'])
    return flask.jsonify(results="Error")


@app.route('/seasons/<season>', methods=['GET', 'POST'])
def seasons(season):
    """

    :param season:
    :return:
    """
    print(flask.request.url_root)
    docs = requests.get(str(flask.request.url_root) + "api/getseasons")
    docs = json.loads(docs.text)
    list_s = db['design_seasons'].get_design_document('design_seasons')
    listseason = []
    for x in range(0, len(list_s['seasons'])):
        name_season = list_s['seasons'][x]['nameSeason']
        listseason.append(name_season)
    if season in listseason:
        items = requests.get(str(flask.request.url_root) + "api/newsampledata/" + str(season))
        items = json.loads(items.text)
        # print items
        if items['results'] == "Error":
            return flask.render_template('empty.html')
        return flask.render_template('seasons.html', items=items['results'], dataSeasons=docs['results'], season=season)
    return 'You want path: %s' % flask.request.url_root


@app.route('/seasons11', methods=['GET', 'POST'])
def seasons11():
    """

    :return:
    """
    # print request.url_root
    # docs = requests.get(str(request.url_root) + "api/getseasons")
    # docs = json.loads(docs.text)
    # if season in  db.keys(remote=True):
    #     items = requests.get(str(request.url_root) + "api/newsampledata/"+str(season))
    #     items = json.loads(items.text)
    #     #print items
    #     if items['results'] == "Error":
    #         return render_template('empty.html')
    return flask.render_template('seasons1.html')
