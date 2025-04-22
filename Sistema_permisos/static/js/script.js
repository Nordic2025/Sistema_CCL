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
    document.getElementById("sidebar ").style.width = "250px";
    document.getElementById("menu-open").style.marginLeft = "250px";
}

function cerrarMenu() {
    const sidebar = document.getElementById("sidebar");
    if (sidebar) {
        sidebar.classList.remove("open");
    }
}












