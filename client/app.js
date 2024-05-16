SERVER_URL='http://127.0.0.1:4000'

function Login(response){
    localStorage.setItem("token",response.credential);
}

function onLinkAdsAcc(){
    token = localStorage.getItem("token");
    window.location.href=`${SERVER_URL}/authorize?token=${token}`;
}

function listAccessibleCustomer(){
    const url = `${SERVER_URL}/customers`;
    const xhr = new XMLHttpRequest();
    xhr.open("GET",url,true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.setRequestHeader("token", localStorage.getItem("token"));
    xhr.send();
    xhr.onload = function() {
        if (xhr.status == 200){
            const response = JSON.parse(xhr.response);
            if ("name" in response && response.name == "INVALID_REFRESH_TOKEN"){
                onLinkAdsAcc();
            }else{
                console.log(response);
            }
        }
    }
}

function createListCustomer(){
    const url = `${SERVER_URL}/create_customers_list`;
    const xhr = new XMLHttpRequest();
    xhr.open("GET",url,true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.setRequestHeader("token", localStorage.getItem("token"));
    xhr.setRequestHeader("customer_id", localStorage.getItem("667-543-7078"));
    xhr.send();
    xhr.onload = function() {
        if (xhr.status == 200){
            const response = JSON.parse(xhr.response);
            if ("name" in response && response.name == "INVALID_REFRESH_TOKEN"){
                onLinkAdsAcc();
            }else{
                console.log(response);
            }
        }
    }
    
}