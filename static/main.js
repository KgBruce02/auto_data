var projects = document.getElementsByClassName('gitlab')
var branches = []
var committer_codes = new Map()
var commit_nums = new Map()
var temp_lines = 0;
var commmit_num = 0;
var project_id = 0;
var branch_name = ""
var gitlab_projects = $('.list_group')
var project_info = $('.tab_content')
var tianji = $('#tianji')
var bms = $('#bms')
var pylai = $('#pylai')
var groupchat = ''
daily_report()
submit_report()

function daily_report() {
    let project_name = ''
    let member_name = ''
    tianji.click(function() {
        document.getElementById('project_name').innerHTML = '天机1.5'
        project_name = 'tianji1.5'
    })
    bms.click(function() {
        document.getElementById('project_name').innerHTML = 'BMS'
        project_name = 'BMS'
    })
    pylai.click(function() {
        document.getElementById('member_name').innerHTML = '赖潘湧'
        member_name = '赖潘湧'
    })
    $('#jasonzhang').click(function() {
        document.getElementById('member_name').innerHTML = '张建生'
        member_name = '张建生'
    })
    $('#dingtao').click(function() {
        document.getElementById('member_name').innerHTML = '陈定涛'
        member_name = '陈定涛'
    })
    $('#weibin').click(function() {
        document.getElementById('member_name').innerHTML = '唐伟斌'
        member_name = '唐伟斌'
    })
    $('#chucheng').click(function() {
        document.getElementById('member_name').innerHTML = '沈楚城'
        member_name = '沈楚城'
    })
    $('#bms_dingtalk').click(function() {
        document.getElementById('group_selected').innerHTML = 'bms'
    })
    $('#submit').click(function() {
        let past_workload = $('#past_workload').val()
        let today_workload = $('#today_workload').val()
        let left_workload = $('#left_workload').val()
        let risk = $('#risk').val()
        $.ajax({
            url: ' http://127.0.0.1:5000/',
            type: 'POST',
            data: {
                project_name: project_name,
                member_name: member_name,
                past_workload: past_workload,
                today_workload: today_workload,
                left_workload: left_workload,
                risk: risk
            },
            success: function(res) {
                console.log(project_name, member_name)
                console.log('success')
            }
        })
    })
}

function submit_report() {
    $('#tianji_dingtalk').click(function() {
        $.ajax({
            url: ' http://127.0.0.1:5000/result',
            type: 'POST',
            data: {
                project_name: 'tianji',
                send_report: 1
            },
            success: function(res) {
                console.log('success')
            }
        })
    })
    $('#clear').click(function() {
        $.ajax({
            url: ' http://127.0.0.1:5000/result',
            type: 'POST',
            data: {
                clear_record: 1
            },
            success: function(res) {
                console.log('success')
            }
        })
    })
}

// function gitlab_append_project(name, id) {
//     html_str = '<a class="list-group-item list-group-item-action" data-toggle="list" href="#' + id + '"' + 'role = "tab" > ' + name + '</a>'
//     gitlab_projects.innerHTML += html_str

// }
// // gitlab data
// $(function() {
//     $.ajax({
//         type: 'GET',
//         url: 'http://gitlab.deepwisdomai.com/api/v4/projects/?access_token=yVz77UDx-b3hSFeXhPkB&per_page=100&page=1',
//         crossDomain: true,
//         async: false,
//         success: function(data) {
//             $.each(data, function(i, project) { // each projects
//                 gitlab_append_project(project.name, project.id)
//                 project_id = project.id
//                 $.ajax({
//                     type: 'GET',
//                     url: 'http://gitlab.deepwisdomai.com/api/v4/projects/' + project_id + '/repository/branches/?access_token=yVz77UDx-b3hSFeXhPkB&per_page=100&page=1',
//                     success: function(data) {
//                         console.log('success')
//                         var branch_index = 0;
//                         $.each(data, function(i, branch) { // branches
//                             committer_codes.clear()
//                             commit_nums.clear()
//                             branches.length = 0
//                             branches.push(branch.name)
//                             if (branch_index === 0) {
//                                 html_str = ' <div class="tab-pane fade"' + 'id="' + project.id + '"' + 'role="tabpanel">'
//                                 html_str += ' <p>Branch名称：' + branch.name + '</p>'
//                                 html_str += ' <table class="table"> <thead><tr><th scope = "col"> # </th> <th scope = "col" > 姓名 </th> <th scope = "col" > 代码行数 </th> <th scope = "col"> commit数量 </th> </tr> </thead> <tbody>'
//                             } else {
//                                 html_str += ' <p>Branch名称：' + branch.name + '</p>'
//                                 html_str += ' <table class="table"> <thead><tr><th scope = "col"> # </th> <th scope = "col" > 姓名 </th> <th scope = "col" > 代码行数 </th> <th scope = "col"> commit数量 </th> </tr> </thead> <tbody>'

//                             }
//                             ++branch_index
//                             branch_name = branch.name
//                             let total_code_lines = gitlab_project(project.id, branch.name)
//                             var i = 1
//                             committer_codes.forEach(function(key, value) {
//                                 if (key != 0) {
//                                     // console.log(value + '的代码数量为' + key)
//                                     html_str += ' <tr><th scope="row">' + i + '</th>'
//                                     html_str += '<td>' + value + '</td>'
//                                     html_str += '<td>' + key + '</td>'
//                                     html_str += '<td>' + commit_nums.get(value) + '</td>'
//                                     html_str += ' </tr>'
//                                     console.log(project.id)
//                                     i = i + 1
//                                 }
//                             })
//                             // project_info.innerHTML += html_str
//                             console.log(branch_index)

//                         })
//                         html_str += ' </tbody></table></div>'
//                         html_str += '</div>'
//                         console.log(html_str)
//                         project_info.innerHTML += html_str
//                     }
//                 })

//             })

//         }
//     })

// });

// function gitlab_project(id, branch_name) {
//     //查询每个成员的代码量
//     let lines_commit = 0
//     let total_lines = 0
//     $.ajax({
//             type: 'GET',
//             url: 'http://gitlab.deepwisdomai.com/api/v4/projects/' + id + '/repository/commits/?access_token=yVz77UDx-b3hSFeXhPkB&ref_name=' + branch_name + '&per_page=100&page=1',
//             async: false,
//             success: function(data) {
//                 // console.log('success', data)
//                 $.each(data, function(i, project) {
//                     // console.log(project.id)
//                     lines_commit = get_code_lines(id, project.id)
//                         // console.log(lines_commit)
//                     total_lines = lines_commit + total_lines
//                 })
//             }
//         })
//         // console.log(total_lines)
//     return total_lines

// };

// function get_code_lines(project_id, commit_id) {
//     var total_lines_added = 0;
//     $.ajax({
//         type: 'GET',
//         url: 'http://gitlab.deepwisdomai.com/api/v4/projects/' + project_id + '/repository/commits/' + commit_id + '/?access_token=yVz77UDx-b3hSFeXhPkB&per_page=100&page=1',
//         async: false,
//         success: function(data) {
//             // console.log('success', data)
//             total_lines_added = data.stats.additions - data.stats.deletions
//                 // console.log('commit id: ' + commmit_num + data.committer_name + '这次commit新增的代码数：')
//                 // console.log(total_lines_added)
//             commmit_num = commmit_num + 1
//             if (!committer_codes.has(data.committer_name)) {
//                 committer_codes.set(data.committer_name, 0)
//             }
//             if (!commit_nums.has(data.committer_name)) {
//                 commit_nums.set(data.committer_name, 0)
//             }
//             temp_lines = 0
//             temp_lines = committer_codes.get(data.committer_name)
//             temp_lines += total_lines_added
//             committer_codes.set(data.committer_name, temp_lines)
//             temp_commit_nums = commit_nums.get(data.committer_name)
//             temp_commit_nums = temp_commit_nums + 1
//             commit_nums.set(data.committer_name, temp_commit_nums)

//         }
//     })
//     return total_lines_added

// };
// code review
// var codereview_container = document.getElementsByClassName('codereview')[0]
//     // open review
// html_str = '<p>待审核的Commit</p>'

// $.ajax({
//     type: 'GET',
//     url: 'http://gitlab.deepwisdomai.com/changes/?access_token=Basic%20aGFucGluZ3pob25nOmdRWGs5OGQrbDRUVWM5TmlmalJVTDV0M05ZaW9iK00yeFZEYzAzSVcvQQ==&q=status:open',
//     dataType: 'jsonp',
//     crossDomain: true,
//     async: false,
//     success: function(data) {
//         html_str += ' <table class="table"> <thead><tr><th scope = "col"> # </th> <th scope = "col" > Subject </th> <th scope = "col" > Status </th> <th scope = "col"> Owner </th>  <th scope = "col" > Status </th> <th scope = "col" > Repo </th> <th scope = "col" > Branch </th> <th scope = "col" > Updated </th></tr> </thead> <tbody>',
//             i = 1,
//             $.each(data, function(i, project) { // Each commit
//                 html_str += ' <tr><th scope="row">' + i + '</th>'
//                 html_str += '<td>' + project.subject + '</td>'
//                 html_str += '<td>' + project.status + '</td>'
//                 html_str += '<td>' + project.owner.id + '</td>'
//                 html_str += '<td>' + project.status + '</td>'
//                 html_str += '<td>' + project.project + '</td>'
//                 html_str += '<td>' + project.branch + '</td>'
//                 html_str += '<td>' + project.updated + '</td>'
//                 html_str += ' </tr>'
//                 i = i + 1
//             })
//         html_str += ' </tbody></table></div>'
//         html_str += '</div>'
//         codereview_container.innerHTML += html_str

//     }

// })