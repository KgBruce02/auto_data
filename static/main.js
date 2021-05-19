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
        let workload_info = $('#workload_info').val()

        // let today_workload = $('#today_workload').val()
        // let left_workload = $('#left_workload').val()
        // let risk = $('#risk').val()
        console.log(workload_info)
        console.log(member_name)
        $.ajax({
            url: ' http://127.0.0.1:5000/',
            type: 'POST',
            data: {
                project_name: project_name,
                member_name: member_name,
                workload_info: workload_info
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
        console.log('cleared')
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