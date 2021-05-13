import json

import requests
from flask import Flask, render_template, request, url_for
from flask_cors import CORS
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
tianji_report = []
bms_report = []
project_ids = []
total_info = []
committer_codes = {}
commit_nums = {}
project_id = ''
branch_name = ''
# 获取cookie response = make_response(jsonfiy(Object)) response.set_cookie('key','value',max_age=3600) response.headers['Access-Control-Allow-Credentials']='true'#设置响应数据的头部，不然无法将response返回给前端 return response
projects = {}


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
            names.append(name)
            num.append(x)
            codes.append(committer_codes[name])
            commits.append(commit_nums[name])
            context = [x, name, committer_codes[name], commit_nums[name]]
            each_person.append(context)
            x = x+1
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
    response = requests.request("GET", url, headers=headers, data=payload)
    dict_data = json.dumps(response.json())
    dict_data = json.loads(dict_data)
    for project in dict_data:
        projects[project['name']] = project['id']
        project_ids.append(project['id'])
    print(project_ids)
    for each_id in project_ids:
        project_id = str(each_id)
        each_project(project_id)
    print(total_info)


gitlab_data()

bms_sprin3_tasks = {'pylai': 6, 'zhengwu': 20, 'chuchengshen': 0}
bms_sprin3_bugs = {'pylai': {'Done': 0, 'In Progress': 0, 'To Do': 0}, 'zhengwu': {
    'Done': 0, 'In Progress': 0, 'To Do': 0}, 'chuchengshen': {'Done': 0, 'In Progress': 0, 'To Do': 0}}
tianji_sprint1_tasks = {'pylai': {'Done': 0, 'In Progress': 0, 'To Do': 0}, 'zhengwu': {
    'Done': 0, 'In Progress': 0, 'To Do': 0}, 'jasonzhang': {'Done': 0, 'In Progress': 0, 'To Do': 0}, 'chendingtao': {'Done': 0, 'In Progress': 0, 'To Do': 0}, 'chuchengshen': {'Done': 0, 'In Progress': 0, 'To Do': 0}}
tianji_sprint1_bugs = {'pylai': {'Done': 0, 'In Progress': 0, 'To Do': 0}, 'zhengwu': {
    'Done': 0, 'In Progress': 0, 'To Do': 0}, 'jasonzhang': {'Done': 0, 'In Progress': 0, 'To Do': 0}, 'chendingtao': {'Done': 0, 'In Progress': 0, 'To Do': 0}, 'chuchengshen': {'Done': 0, 'In Progress': 0, 'To Do': 0}}
tianji_sprint2_tasks = {'pylai': {'Done': 0, 'In Progress': 0, 'To Do': 0}, 'zhengwu': {
    'Done': 0, 'In Progress': 0, 'To Do': 0}, 'jasonzhang': {'Done': 0, 'In Progress': 0, 'To Do': 0}, 'chendingtao': {'Done': 0, 'In Progress': 0, 'To Do': 0}}
tianji_sprint2_bugs = {'pylai': {'Done': 0, 'In Progress': 0, 'To Do': 0}, 'zhengwu': {
    'Done': 0, 'In Progress': 0, 'To Do': 0}, 'jasonzhang': {'Done': 0, 'In Progress': 0, 'To Do': 0}, 'chendingtao': {'Done': 0, 'In Progress': 0, 'To Do': 0}}
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
    while i < 5:
        if i == 0:
            assignee = "pylai"
        elif i == 1:
            assignee = "zhengwu"
        elif i == 2:
            assignee = "jasonzhang"
        elif i == 3:
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
    while i < 5:
        if i == 0:
            assignee = "pylai"
        elif i == 1:
            assignee = "zhengwu"
        elif i == 2:
            assignee = "jasonzhang"
        elif i == 3:
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
        for value in tianji_sprint1_tasks[name].values():
            msg.append(value)
        for value in tianji_sprint1_bugs[name].values():
            msg.append(value)
        num = num + 1
        tianji_sprint1_context.append(msg)
    # tianji sprint2 tasks
    i = 0  # track assignee
    k = 0  # track status
    status = ""
    while i < 5:
        if i == 0:
            assignee = "pylai"
        elif i == 1:
            assignee = "zhengwu"
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
    while i < 4:
        if i == 0:
            assignee = "pylai"
        elif i == 1:
            assignee = "zhengwu"
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
        msg = []
        msg = [num, name]
        for value in tianji_sprint2_tasks[name].values():
            msg.append(value)
        for value in tianji_sprint2_bugs[name].values():
            msg.append(value)
        num = num + 1
        tianji_sprint2_context.append(msg)


jira_data()


@app.route('/', methods=['POST', 'GET'])
def index():
    project_name = ''
    member_name = ''
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        member_name = request.form.get('member_name')
        past_workload = request.form.get('past_workload')
        today_workload = request.form.get('today_workload')
        left_workload = request.form.get('left_workload')
        risk = request.form.get('risk')
        member_report = member_name+': ' + \
            past_workload+' '+today_workload+' '+left_workload+' '+risk
        if(project_name == 'tianji1.5'):
            tianji_report.append(member_report)
        elif (project_name == 'BMS'):
            bms_report.append(member_report)
    return render_template("index.html", gitlab_projects=projects, total=total_info)


@app.route('/result', methods=['POST', 'GET'])
def result():
    reports = tianji_report
    message = '#### 总结 @18153953579\n'
    for i in tianji_report:
        message += '> ##### ' + i+'\n'
    clear = ''
    send_report = ''
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
    return render_template("result.html", tianji_reports=reports)


@app.route('/jira', methods=['POST', 'GET'])
def jira():
    return render_template("jira.html", bms_sprint3=bms_sprint3_context, tianji_sprint1=tianji_sprint1_context, tianji_sprint2=tianji_sprint2_context)


if __name__ == '__main__':
    app.run(debug=True)
