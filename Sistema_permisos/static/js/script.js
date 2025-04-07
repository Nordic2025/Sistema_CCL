//Alerta
function mensaje(type, texto) {
    let icon = 'info';  // Valor por defecto

    if (type === 'success') {
        icon = 'success';
    } else if (type === 'error') {
        icon = 'error';
    }
    else if (type === 'warning') {
        icon = 'warning';
    }


    Swal.fire({
        position: "center",
        icon: type,
        title: texto,
        showConfirmButton: false,
        timer: 1500
    });
}




//Menu lateral

function abrirMenu() {
    document.getElementById("menuLateral").style.width = "250px";
    document.getElementById("menu-open").style.marginLeft = "250px";
}

function cerrarMenu() {
    document.getElementById("menuLateral").style.width = "0";
    document.getElementById("menu-open").style.marginLeft = "0";
}












