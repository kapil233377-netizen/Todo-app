console.log("JavaScript Connected Successfully");


function showMessage(){
    alert("Welcome to My Todo App 🚀");
}


// Auto remove flash messages

document.addEventListener("DOMContentLoaded", function(){

    setTimeout(function(){

        let alerts = document.querySelectorAll(".flash-message");

        alerts.forEach(function(alert){

            alert.style.transition = "0.5s";
            alert.style.opacity = "0";

            setTimeout(function(){
                alert.remove();
            }, 500);

        });

    }, 3000);

});