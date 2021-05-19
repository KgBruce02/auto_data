import json
import time
import requests
from flask import Flask, render_template, request, url_for
from flask_cors import CORS
from elasticsearch import Elasticsearch
from datetime import datetime
from elasticsearch import helpers
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
es = Elasticsearch('http://192.168.50.155:9200/')
app = Flask(__name__)
# CORS(app, resources={r"/api/*": {"origins": "*"}})
tianji_report = []
bms_report = []
project_ids = []
total_info = []
es_data = []
es_jira_data = []
created_time = time.asctime(time.localtime(time.time()))
created_time = datetime.strptime(
    created_time, '%a %b %d %H:%M:%S %Y')
committer_codes = {}
commit_nums = {}
project_id = ''
branch_name = ''
project_name = ''
# 获取cookie response = make_response(jsonfiy(Object)) response.set_cookie('key','value',max_age=3600) response.headers['Access-Control-Allow-Credentials']='true'#设置响应数据的头部，不然无法将response返回给前端 return response
projects = {}


class Config(object):
    JOBS = [
        {
            'id': 'job1',
            'func': '__main__:loop',  # 方法名
            'args': (),  # 入参
            'trigger': 'cron',  # trigger type
            'day_of_week': 'mon-fri',              # 每周1至周5早上6点执行
            'hour': 6,
            'minute': 00
        },
        {
            'id': 'job2',
            'func': '__main__:loop',  # 方法名
            'args': (),  # 入参
            'trigger': 'cron',  # trigger type
            'day_of_week': 'mon-fri',
            'hour': 12,
            'minute': 30
        }

    ]
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'


def search_gitlab_data(project_id, branch_name, name, type):
    # type = 1: last day, 2: last week, 3: last month
    gte = ''
    if type == 1:
        gte = 'now-1d'
    elif type == 2:
        gte = 'now-1w'
    else:
        gte = 'now-4w'

    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "update_time": {

                                "gte": gte
                            }
                        }
                    },
                    {
                        "match": {
                            "name": name
                        }
                    },
                    {
                        "match": {
                            "branch_name": branch_name
                        }
                    },
                    {
                        "match": {
                            "project_id": project_id
                        }
                    }
                ],
                "must_not": [],
                "should": []
            }
        },
        "from": 0,
        "size": 1000,
        "sort": [],
        "aggs": {}
    }
    result = es.search(index="gitlab_test4", body=body)
    result_dict = {
        'add_codes': result['hits']['hits'][0]['_source']['code_lines'],
        'add_commits': result['hits']['hits'][0]['_source']['commit_num']
    }
    return result_dict


def search_jira_data(sprint_name, name, type):
    # type = 1: last day, 2: last week, 3: last month
    gte = ''
    if type == 1:
        gte = 'now-1d'
    elif type == 2:
        gte = 'now-1w'
    else:
        gte = 'now-4w'

    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "update_time": {

                                "gte": gte
                            }
                        }
                    },
                    {
                        "match": {
                            "name": name
                        }
                    },
                    {
                        "match": {
                            "sprint_name": sprint_name
                        }
                    },
                ],
                "must_not": [],
                "should": []
            }
        },
        "from": 0,
        "size": 1000,
        "sort": [],
        "aggs": {}
    }
    result = es.search(index="gitlab_test3", body=body)
    result_dict = {
        'add_codes': result['hits']['hits'][0]['_source']['code_lines'],
        'add_commits': result['hits']['hits'][0]['_source']['commit_num']
    }
    return result_dict


def get_code_lines(id, commit_id):
    total_lines_added = 0
    url = 'http://gitlab.deepwisdomai.com/api/v4/projects/'+id+'/repository/commits/' + \
        commit_id+'/?access_token=yVz77UDx-b3hSFeXhPkB&per_page=100&page=1'
    headers = {}
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    dict_data = json.dumps(response.json())
    dict_data = json.loads(dict_data)
    total_lines_added = dict_data['stats']['additions'] - \
        dict_data['stats']['deletions']
    commit_name = dict_data['committer_name']
    if commit_name not in commit_nums:
        commit_nums[commit_name] = 0
    if commit_name not in committer_codes:
        committer_codes[commit_name] = 0
    temp_lines = 0
    temp_lines = committer_codes[commit_name]
    temp_lines += total_lines_added
    committer_codes[commit_name] = temp_lines
    temp_commit_nums = commit_nums[commit_name]
    temp_commit_nums += 1
    commit_nums[commit_name] = temp_commit_nums
    return total_lines_added


def gitlab_project(id, branch_name):
    lines_commit = 0
    total_lines = 0
    url = 'http://gitlab.deepwisdomai.com/api/v4/projects/'+id + \
        '/repository/commits/?access_token=yVz77UDx-b3hSFeXhPkB&ref_name=' + \
        branch_name+'&per_page=100&page=1'
    headers = {}
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    dict_data = json.dumps(response.json())
    dict_data = json.loads(dict_data)
    for commit in dict_data:
        commit_id = str(commit['id'])
        lines_commit = get_code_lines(id, commit_id)
        total_lines = lines_commit+total_lines
    return total_lines


def each_project(id):
    url = 'http://gitlab.deepwisdomai.com/api/v4/projects/'+id + \
        '/repository/branches/?access_token=yVz77UDx-b3hSFeXhPkB&per_page=100&page=1'
    print(url)
    headers = {}
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    dict_data = json.dumps(response.json())
    dict_data = json.loads(dict_data)
    branch_index = 0
    project_id = id
    names = []
    codes = []
    commits = []
    num = []
    global total_info
    branches = []
    not_first_branch = False
    branch_size = len(dict_data)
    # print(dict_data)
    for branch in dict_data:
        last_branch = False
        print('Current branch: '+branch['name']+'\n')
        if len(branches) >= 1:
            not_first_branch = True

        print(not_first_branch)
        # print(branch)
        committer_codes.clear()
        commit_nums.clear()
        branches.append(branch['name'])
        if len(branches) == branch_size:
            last_branch = True
        branch_name = branch['name']
        gitlab_project(project_id, branch_name)
        x = 1
        each_person = []

        for name in committer_codes.keys():
            localtime = time.asctime(time.localtime(time.time()))
            localtime = datetime.strptime(
                localtime, '%a %b %d %H:%M:%S %Y')
            global created_time
            global project_name
            names.append(name)
            num.append(x)
            codes.append(committer_codes[name])
            commits.append(commit_nums[name])
            # codes_last_day = committer_codes[name]
            # codes_last_week = committer_codes[name]
            # codes_last_month = committer_codes[name]
            # commits_last_day = commit_nums[name]
            # commits_last_week = commit_nums[name]
            # commits_last_month = commit_nums[name]
            codes_last_day = committer_codes[name] - search_gitlab_data(
                project_id, branch_name, name, 1)['add_codes']
            codes_last_week = committer_codes[name] - search_gitlab_data(
                project_id, branch_name, name, 2)['add_codes']
            codes_last_month = committer_codes[name] - search_gitlab_data(
                project_id, branch_name, name, 3)['add_codes']
            commits_last_day = commit_nums[name]-search_gitlab_data(
                project_id, branch_name, name, 1)['add_commits']
            commits_last_week = commit_nums[name]-search_gitlab_data(
                project_id, branch_name, name, 2)['add_commits']
            commits_last_month = commit_nums[name]-search_gitlab_data(
                project_id, branch_name, name, 3)['add_commits']
            context = [x, name, committer_codes[name], commit_nums[name], codes_last_day,
                       codes_last_week, codes_last_month, commits_last_day, commits_last_week, commits_last_month]
            each_person.append(context)
            x = x+1

            es_dict = {
                'project_id': project_id,
                'branch_name': branch_name,
                'name': name,
                'project_name': project_name,
                'code_lines': committer_codes[name],
                'commit_num': commit_nums[name],
                'codes_added_last_day': codes_last_day,
                'codes_added_last_week': codes_last_week,
                'codes_added_last_month': codes_last_month,
                'commits_added_last_day': commits_last_day,
                'commits_added_last_week': commits_last_week,
                'commits_added_last_month': commits_last_month,
                'created_time': created_time,
                'update_time': localtime,
            }
            es_data.append(es_dict)
        my_dict = {
            'project_id': project_id,
            'branch_name': branch_name,
            'not_first_branch': not_first_branch,
            'last_branch': last_branch,

            # 'codes': codes,
            # 'commits': commits,
            'num': num,
            'each_person': each_person
        }
        total_info.append(my_dict)

    print('Branch name: ')
    print(branches)
    print('\n')


def gitlab_data():
    url = 'http://gitlab.deepwisdomai.com/api/v4/projects/?access_token=yVz77UDx-b3hSFeXhPkB&per_page=100&page=1'
    headers = {}
    payload = {}
    global projects
    response = requests.request("GET", url, headers=headers, data=payload)
    dict_data = json.dumps(response.json())
    dict_data = json.loads(dict_data)
    for project in dict_data:
        projects[project['name']] = str(project['id'])
        project_ids.append(project['id'])

    global project_name
    for each_id in project_ids:
        project_id = str(each_id)
        project_name = list(projects.keys())[list(
            projects.values()).index(project_id)]

        each_project(project_id)


bms_sprin3_tasks = {'pylai': 6, 'zhengwu': 20, 'chuchengshen': 0}
bms_sprin3_bugs = {'pylai': {'Done': 0, 'In Progress': 0, 'To Do': 0}, 'zhengwu': {
    'Done': 0, 'In Progress': 0, 'To Do': 0}, 'chuchengshen': {'Done': 0, 'In Progress': 0, 'To Do': 0}}
tianji_sprint1_tasks = {'pylai': {'Done': 0, 'In Progress': 0, 'To Do': 0}, 'zhengwu': {
    'Done': 0, 'In Progress': 0, 'To Do': 0}, 'jasonzhang': {'Done': 0, 'In Progress': 0, 'To Do': 0}, 'chendingtao': {'Done': 0, 'In Progress': 0, 'To Do': 0}, 'chuchengshen': {'Done': 0, 'In Progress': 0, 'To Do': 0}}
tianji_sprint1_bugs = {'pylai': {'Done': 0, 'In Progress': 0, 'To Do': 0}, 'zhengwu': {
    'Done': 0, 'In Progress': 0, 'To Do': 0}, 'jasonzhang': {'Done': 0, 'In Progress': 0, 'To Do': 0}, 'chendingtao': {'Done': 0, 'In Progress': 0, 'To Do': 0}, 'chuchengshen': {'Done': 0, 'In Progress': 0, 'To Do': 0}}
tianji_sprint2_tasks = {'pylai': {'Done': 0, 'In Progress': 0, 'To Do': 0}, 'jasonzhang': {
    'Done': 0, 'In Progress': 0, 'To Do': 0}, 'chendingtao': {'Done': 0, 'In Progress': 0, 'To Do': 0}}
tianji_sprint2_bugs = {'pylai': {'Done': 0, 'In Progress': 0, 'To Do': 0}, 'jasonzhang': {
    'Done': 0, 'In Progress': 0, 'To Do': 0}, 'chendingtao': {'Done': 0, 'In Progress': 0, 'To Do': 0}}
bms_sprint3_context = []
tianji_sprint1_context = []
tianji_sprint2_context = []


def jira_data():
    print('getting jira data')
    i = 0
    while i < 3:
        if i == 0:
            assignee = "pylai"
        elif i == 1:
            assignee = "zhengwu"
        else:
            assignee = "chuchengshen"
        url = '''http://jira.oa.com/rest/api/2/search?jql=project = FZTJ AND issuetype in (subTaskIssueTypes(), Task) AND status in ("To Do", "In Progress", Done) AND Sprint = 81 AND assignee in ('''+assignee+')'
        print(url)
        payload = {}
        headers = {
            'Authorization': 'Basic aGFucGluZ3pob25nOkFwdHg0ODY5',
            'Cookie': 'JSESSIONID=4EF85B48EBED4EE7F22B0B810D95716C; atlassian.xsrf.token=BCMM-NRT9-QD3C-KY5X_91d02e5e2fd2ebf3d9bc06d4bbafda623ba6830b_lin'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        dict_data = json.dumps(response.json())
        dict_data = json.loads(dict_data)
        num = dict_data["total"]
        print(dict_data['issues'][4]['fields']['customfield_10006'])
        if i == 0:
            bms_sprin3_tasks["pylai"] = num
        elif i == 1:
            bms_sprin3_tasks["zhengwu"] = num
        else:
            bms_sprin3_tasks["chuchengshen"] = num
        i = i + 1
    # bms sprint3 bugs
    i = 0  # track assignee
    k = 0  # track status
    status = ""
    while i < 3:
        if i == 0:
            assignee = "pylai"
        elif i == 1:
            assignee = "zhengwu"
        else:
            assignee = "chuchengshen"
        k = 0
        while k < 3:
            if k == 0:
                status = "Done"
            elif k == 1:
                status = "In Progress"
            else:
                status = "To Do"
            url = '''http://jira.oa.com/rest/api/2/search?jql=project = FZTJ AND issuetype = Bug AND status ="''' + \
                status + '''"''' + \
                ''' AND Sprint = 81 AND assignee in ('''+assignee+')'

            print(url)
            payload = {}
            headers = {
                'Authorization': 'Basic aGFucGluZ3pob25nOkFwdHg0ODY5',
                'Cookie': 'JSESSIONID=4EF85B48EBED4EE7F22B0B810D95716C; atlassian.xsrf.token=BCMM-NRT9-QD3C-KY5X_91d02e5e2fd2ebf3d9bc06d4bbafda623ba6830b_lin'
            }
            response = requests.request(
                "GET", url, headers=headers, data=payload)
            dict_data = json.dumps(response.json())
            dict_data = json.loads(dict_data)
            num = dict_data["total"]
            if k == 0:
                bms_sprin3_bugs[assignee]['Done'] = num
            elif k == 1:
                bms_sprin3_bugs[assignee]['In Progress'] = num
            else:
                bms_sprin3_bugs[assignee]['To Do'] = num
            k = k + 1
        i = i + 1
    global bms_sprint3_context
    num = 1
    for name in bms_sprin3_bugs.keys():
        msg = []
        msg = [num, name, bms_sprin3_tasks[name], 0, 0]
        for value in bms_sprin3_bugs[name].values():
            msg.append(value)
        num = num + 1
        bms_sprint3_context.append(msg)
    # print(bms_sprin3_bugs)
    # tianji sprint1 tasks
    i = 0  # track assignee
    k = 0  # track status
    status = ""
    while i < 4:
        if i == 0:
            assignee = "pylai"
        elif i == 1:
            assignee = "jasonzhang"
        elif i == 2:
            assignee = "chendingtao"
        else:
            assignee = "chuchengshen"
        k = 0
        while k < 3:
            if k == 0:
                status = "Done"
            elif k == 1:
                status = "In Progress"
            else:
                status = "To Do"
            url = '''http://jira.oa.com/rest/api/2/search?jql=project = FZTJ AND issuetype in (subTaskIssueTypes(), Task) AND status ="''' + \
                status + '''"''' + \
                ''' AND Sprint = 85 AND assignee in ('''+assignee+')'
            print(url)
            payload = {}
            headers = {
                'Authorization': 'Basic aGFucGluZ3pob25nOkFwdHg0ODY5',
                'Cookie': 'JSESSIONID=4EF85B48EBED4EE7F22B0B810D95716C; atlassian.xsrf.token=BCMM-NRT9-QD3C-KY5X_91d02e5e2fd2ebf3d9bc06d4bbafda623ba6830b_lin'
            }
            response = requests.request(
                "GET", url, headers=headers, data=payload)
            dict_data = json.dumps(response.json())
            dict_data = json.loads(dict_data)
            num = dict_data["total"]
            if k == 0:
                tianji_sprint1_tasks[assignee]['Done'] = num
            elif k == 1:
                tianji_sprint1_tasks[assignee]['In Progress'] = num
            else:
                tianji_sprint1_tasks[assignee]['To Do'] = num
            k = k + 1
        i = i + 1
    # tianji sprint1 bugs
    i = 0  # track assignee
    k = 0  # track status
    status = ""
    while i < 4:
        if i == 0:
            assignee = "pylai"
        elif i == 1:
            assignee = "jasonzhang"
        elif i == 2:
            assignee = "chendingtao"
        else:
            assignee = "chuchengshen"
        k = 0
        while k < 3:
            if k == 0:
                status = "Done"
            elif k == 1:
                status = "In Progress"
            else:
                status = "To Do"
            url = '''http://jira.oa.com/rest/api/2/search?jql=project = FZTJ AND issuetype = Bug AND status ="''' + \
                status + '''"''' + \
                ''' AND Sprint = 85 AND assignee in ('''+assignee+')'
            print(url)
            # "customfield_10006"
            # "customfield_10401"
            payload = {}
            headers = {
                'Authorization': 'Basic aGFucGluZ3pob25nOkFwdHg0ODY5',
                'Cookie': 'JSESSIONID=4EF85B48EBED4EE7F22B0B810D95716C; atlassian.xsrf.token=BCMM-NRT9-QD3C-KY5X_91d02e5e2fd2ebf3d9bc06d4bbafda623ba6830b_lin'
            }
            response = requests.request(
                "GET", url, headers=headers, data=payload)
            dict_data = json.dumps(response.json())
            dict_data = json.loads(dict_data)
            num = dict_data["total"]
            if k == 0:
                tianji_sprint1_bugs[assignee]['Done'] = num
            elif k == 1:
                tianji_sprint1_bugs[assignee]['In Progress'] = num
            else:
                tianji_sprint1_bugs[assignee]['To Do'] = num
            k = k + 1
        i = i + 1
    global tianji_sprint1_context
    num = 1

    for name in tianji_sprint1_bugs.keys():

        msg = []
        msg = [num, name]
        x = 0
        localtime = time.asctime(time.localtime(time.time()))
        localtime = datetime.strptime(
            localtime, '%a %b %d %H:%M:%S %Y')
        es_dict = {'sprint_name': 'tianji1.5_sprint1', 'name': name, 'tasks_done': 0, 'tasks_In_progress': 0, 'tasks_to_do': 0,
                   'Bugs_done': 0, 'Bugs_In_progress': 0, 'Bugs_to_do': 0, 'created_time': created_time, 'update_time': localtime}
        for value in tianji_sprint1_tasks[name].values():
            if x == 0:
                es_dict['tasks_done'] = value
            elif x == 1:
                es_dict['tasks_In_progress'] = value
            else:
                es_dict['tasks_to_do'] = value
            x = x + 1
            msg.append(value)
        x = 0
        for value in tianji_sprint1_bugs[name].values():
            if x == 0:
                es_dict['Bugs_done'] = value
            elif x == 1:
                es_dict['Bugs_In_progress'] = value
            else:
                es_dict['Bugs_to_do'] = value
            x = x + 1
            msg.append(value)
        num = num + 1
        tianji_sprint1_context.append(msg)
        es_jira_data.append(es_dict)
    # tianji sprint2 tasks
    i = 0  # track assignee
    k = 0  # track status
    status = ""
    while i < 3:
        if i == 0:
            assignee = "pylai"
        elif i == 1:
            assignee = "jasonzhang"
        else:
            assignee = "chendingtao"
        k = 0
        while k < 3:
            if k == 0:
                status = "Done"
            elif k == 1:
                status = "In Progress"
            else:
                status = "To Do"
            url = '''http://jira.oa.com/rest/api/2/search?jql=project = FZTJ AND issuetype in (subTaskIssueTypes(), Task) AND status ="''' + \
                status + '''"''' + \
                ''' AND Sprint = 86 AND assignee in ('''+assignee+')'
            print(url)
            payload = {}
            headers = {
                'Authorization': 'Basic aGFucGluZ3pob25nOkFwdHg0ODY5',
                'Cookie': 'JSESSIONID=4EF85B48EBED4EE7F22B0B810D95716C; atlassian.xsrf.token=BCMM-NRT9-QD3C-KY5X_91d02e5e2fd2ebf3d9bc06d4bbafda623ba6830b_lin'
            }
            response = requests.request(
                "GET", url, headers=headers, data=payload)
            dict_data = json.dumps(response.json())
            dict_data = json.loads(dict_data)
            num = dict_data["total"]
            if k == 0:
                tianji_sprint2_tasks[assignee]['Done'] = num
            elif k == 1:
                tianji_sprint2_tasks[assignee]['In Progress'] = num
            else:
                tianji_sprint2_tasks[assignee]['To Do'] = num
            k = k + 1
        i = i + 1
    # tianji sprint2 bugs
    i = 0  # track assignee
    k = 0  # track status
    status = ""
    while i < 3:
        if i == 0:
            assignee = "pylai"
        elif i == 2:
            assignee = "jasonzhang"
        else:
            assignee = "chendingtao"
        k = 0
        while k < 3:
            if k == 0:
                status = "Done"
            elif k == 1:
                status = "In Progress"
            else:
                status = "To Do"
            url = '''http://jira.oa.com/rest/api/2/search?jql=project = FZTJ AND issuetype = Bug AND status ="''' + \
                status + '''"''' + \
                ''' AND Sprint = 86 AND assignee in ('''+assignee+')'
            print(url)
            payload = {}
            headers = {
                'Authorization': 'Basic aGFucGluZ3pob25nOkFwdHg0ODY5',
                'Cookie': 'JSESSIONID=4EF85B48EBED4EE7F22B0B810D95716C; atlassian.xsrf.token=BCMM-NRT9-QD3C-KY5X_91d02e5e2fd2ebf3d9bc06d4bbafda623ba6830b_lin'
            }
            response = requests.request(
                "GET", url, headers=headers, data=payload)
            dict_data = json.dumps(response.json())
            dict_data = json.loads(dict_data)
            num = dict_data["total"]
            if k == 0:
                tianji_sprint2_bugs[assignee]['Done'] = num
            elif k == 1:
                tianji_sprint2_bugs[assignee]['In Progress'] = num
            else:
                tianji_sprint2_bugs[assignee]['To Do'] = num
            k = k + 1
        i = i + 1
    global tianji_sprint2_context
    num = 1
    for name in tianji_sprint2_bugs.keys():
        localtime = time.asctime(time.localtime(time.time()))
        localtime = datetime.strptime(
            localtime, '%a %b %d %H:%M:%S %Y')
        es_dict = {'sprint_name': 'tianji1.5_sprint2', 'name': name, 'tasks_done': 0, 'tasks_In_progress': 0, 'tasks_to_do': 0,
                   'Bugs_done': 0, 'Bugs_In_progress': 0, 'Bugs_to_do': 0, 'created_time': created_time, 'update_time': localtime}
        msg = []
        msg = [num, name]
        x = 0
        for value in tianji_sprint2_tasks[name].values():
            if x == 0:
                es_dict['tasks_done'] = value
            elif x == 1:
                es_dict['tasks_In_progress'] = value
            else:
                es_dict['tasks_to_do'] = value
            x = x + 1
            msg.append(value)
        for value in tianji_sprint2_bugs[name].values():
            if x == 0:
                es_dict['Bugs_done'] = value
            elif x == 1:
                es_dict['Bugs_In_progress'] = value
            else:
                es_dict['Bugs_to_do'] = value
            x = x + 1
            msg.append(value)
        num = num + 1
        tianji_sprint2_context.append(msg)
        es_jira_data.append(es_dict)


workload_es_dict = []


def get_yesterday_workload():
    assignee = ''
    i = 0
    while i < 3:
        if i == 0:
            assignee = "pylai"
        elif i == 2:
            assignee = "jasonzhang"
        else:
            assignee = "chendingtao"
        i = i + 1
        url = '''http://jira.oa.com/rest/api/2/search?jql=project = FZTJ AND issuetype in (subTaskIssueTypes(), Task) AND status ="''' + \
            'Done' + '''"''' + \
            ''' AND Sprint = 86  AND updated >= -1d AND assignee in (''' + \
            assignee+')'
        print(url)
        payload = {}
        headers = {
            'Authorization': 'Basic aGFucGluZ3pob25nOkFwdHg0ODY5',
            'Cookie': 'JSESSIONID=4EF85B48EBED4EE7F22B0B810D95716C; atlassian.xsrf.token=BCMM-NRT9-QD3C-KY5X_91d02e5e2fd2ebf3d9bc06d4bbafda623ba6830b_lin'
        }
        response = requests.request(
            "GET", url, headers=headers, data=payload)
        dict_data = json.dumps(response.json())
        dict_data = json.loads(dict_data)
        num = dict_data["total"]
        workload = 0
        for issue in dict_data['issues']:
            workload += issue['fields']['customfield_10006']
        url = '''http://jira.oa.com/rest/api/2/search?jql=project = FZTJ AND issuetype in (subTaskIssueTypes(), Task) AND status ="''' + \
            'Done' + '''"''' + \
            ''' AND Sprint = 85  AND updated >= -1d AND assignee in (''' + \
            assignee+')'
        print(url)
        payload = {}
        headers = {
            'Authorization': 'Basic aGFucGluZ3pob25nOkFwdHg0ODY5',
            'Cookie': 'JSESSIONID=4EF85B48EBED4EE7F22B0B810D95716C; atlassian.xsrf.token=BCMM-NRT9-QD3C-KY5X_91d02e5e2fd2ebf3d9bc06d4bbafda623ba6830b_lin'
        }

        response = requests.request(
            "GET", url, headers=headers, data=payload)
        dict_data = json.dumps(response.json())
        dict_data = json.loads(dict_data)
        num += dict_data['total']
        for issue in dict_data['issues']:
            workload += issue['fields']['customfield_10006']
        localtime = time.asctime(time.localtime(time.time()))
        localtime = datetime.strptime(
            localtime, '%a %b %d %H:%M:%S %Y')
        es_dict = {
            'project': 'tianji1.5',
            'name': assignee,
            'tasks_done': num,
            'workload_done': workload,
            'update_time': localtime
        }
        workload_es_dict.append(es_dict)
    print(workload_es_dict)


def generator():
    for row in es_data:
        row['project_id'] = int(row['project_id'])
        yield row


def jira_generator():
    for row in es_jira_data:
        yield {
            '_index': 'jira_test1',
            '_source': row
        }


def daily_generator():
    for row in workload_es_dict:
        yield {
            '_index': 'jira_daily_report',
            '_source': row
        }


def send_es():
    es.indices.create(index='gitlab_test4', ignore=400)
    helpers.bulk(es, generator(), index='gitlab_test4',
                 raise_on_exception=False, raise_on_error=False)
    # mapping = {
    #     "mappings": {
    #         "properties": {
    #             "branch_name": {
    #                 "type": "keyword",
    #             },
    #             "project_name": {
    #                 "type": "keyword",
    #             },
    #             "code_lines": {
    #                 "type": "integer"
    #             },
    #             "commit_num": {
    #                 "type": "integer"
    #             },
    #             "name": {
    #                 "type": "keyword",
    #             },
    #             "project_id": {
    #                 "type": "integer"
    #             }
    #         },

    #     }
    # }
    # url = 'http://192.168.50.155:9200/gitlab_test3'
    # r = requests.put(url=url, json=mapping)
    # print(es_jira_data)
    es.indices.create(index='jira_test1', ignore=400)
    helpers.bulk(es, jira_generator(), index='jira_test1',
                 raise_on_exception=False, raise_on_error=False)
    es.indices.create(index='jira_daily_report', ignore=400)
    helpers.bulk(es, daily_generator(), index='jira_daily_report',
                 raise_on_exception=False, raise_on_error=False)


@app.route('/', methods=['POST', 'GET'])
def index():
    project_name = ''
    member_name = ''
    workload_info = ''
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        workload_info = request.form.get('workload_info')
        member_name = request.form.get('member_name')
        # print(project_name, '    ', workload_info, '   ', member_name)
        # today_workload = request.form.get('today_workload')
        # left_workload = request.form.get('left_workload')
        # risk = request.form.get('risk')
        member_report = member_name + ' 附加信息及风险：  '+workload_info
        print(member_report)
        if(project_name == 'tianji1.5'):
            tianji_report.append(member_report)
        elif (project_name == 'BMS'):
            bms_report.append(member_report)
    return render_template("index.html", gitlab_projects=projects, total=total_info)


@app.route('/result', methods=['POST', 'GET'])
def result():
    reports = tianji_report
    message = '#### 总结 @18153953579\n'
    for item in workload_es_dict:
        message += '> ##### 姓名：'+item['name']+'  昨日关闭的任务数：' + \
            str(item['tasks_done'])+'  昨日完成的工作量： ' + \
            str(item['workload_done'])+'\n'
    for i in tianji_report:
        message += '> ##### ' + i+'\n'
    message += '> #### 每日报告详情(https://127.0.0.1:5000)\n'
    clear = ''
    send_report = ''
    print(message)
    # print(workload_es_dict)
    if request.method == 'POST':
        clear = request.form.get('clear_record')
        send_report = request.form.get('send_report')
        if send_report == '1':
            webhook = "https://oapi.dingtalk.com/robot/send?access_token=9c9f9bd668042b077bc1e37d53e5fc39c7e0365d5c3ec0e85d722b63fef600ac"
            header = {
                "Content-Type": "application/json",
                "Charset": "UTF-8"
            }
            message = {
                "msgtype": "markdown",
                "markdown": {
                    "title": "test",
                    "text": message
                },
                "at": {"atMobiles": ["18153953579", "18750220281"]}
            }

            message_json = json.dumps(message)
            info = requests.post(
                url=webhook, data=message_json, headers=header)
        if clear == '1':
            tianji_report.clear()
            print('cleared')
        print(reports)
    return render_template("result.html", tianji_reports=reports, workload=workload_es_dict)


@app.route('/jira', methods=['POST', 'GET'])
def jira():
    return render_template("jira.html", bms_sprint3=bms_sprint3_context, tianji_sprint1=tianji_sprint1_context, tianji_sprint2=tianji_sprint2_context)


def method_test(a, b):
    print(a+b)


def loop():
    gitlab_data()
    jira_data()
    get_yesterday_workload()
    send_es()


app.config.from_object(Config())

if __name__ == '__main__':
    scheduler = APScheduler(BackgroundScheduler(timezone="Asia/Shanghai"))
    scheduler.init_app(app)
    scheduler.start()
    app.run(debug=False)
