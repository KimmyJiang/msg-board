function add_msg(text, image){
    let new_msg = `<div class="box">
    <div>${text}</div>
    <img src="https://${image}"/>
    <hr/>
    </div>`

    msg_list.innerHTML = new_msg + msg_list.innerHTML;

}


let msg_list = document.querySelector("#msg_list");
msg_list.innerHTML = '';

let leave_btn = document.querySelector("#leave_btn");
leave_btn.addEventListener("click", function(e){
    e.preventDefault();

    let formElem = document.querySelector("#leave_msg");
    let file = document.querySelector("#leave_file");
    let text = document.querySelector("#leave_text");

    let formData = new FormData(formElem)
    let url = "/api/msg";
    

    if (!file.value | !text.value ) {
        alert("欄位不得為空");
    } 
    
    if (text.value && file.value) {

        fetch(url, {
            method: "POST",
            body: formData
        }).then(function(response){
            return response.json();
        }).then(function(res){
            add_msg(res[0][0],res[0][1]);
            file.value = '';
            text.value = '';
        })
    }
});


window.onload = function(){
    fetch("/api/msglist")
    .then(function(response){
        return response.json();
    }).then(function(res){
        show_msg = ''
        for (let i = 0; i < res.length ; i++){
            show_msg += `<div class="box">
            <div>${res[i][0]}</div>
            <img src="https://${res[i][1]}"/>
            <hr/>
            </div>`
        }
        msg_list.innerHTML = show_msg;
    })

}
