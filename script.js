function predictPlant() {
    let plantName = document.getElementById("plantInput").value;

    if (!plantName) {
        alert("Please enter a plant name!");
        return;
    }

    fetch("/predict", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ plant_name: plantName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }

        document.getElementById("plantName").textContent = "🌿 " + data.plant_name;
        document.getElementById("plantInfo").textContent = "📖Medical Use | cures : " + data.info;
        

        let plantImage = document.getElementById("plantImage");
        if (data.image) {
            plantImage.src = "data:image/jpeg;base64," + data.image;
            plantImage.style.display = "block";
        } else {
            plantImage.style.display = "none";
        }

        // Add fade-in effect
        document.getElementById("result").classList.add("visible");
    })
    .catch(error => console.error("Error:", error));
}
// var bar=document.getElementById("bars")
// var navs=document.getElementById("newone");
// function show()
// {
//     bar.style.display="none;"
// }
// function show() {
//     let nav = document.getElementById("newone");
//         nav.style.display = "block";
//         nav.style.display = "flex";        
//         // nav.style.flexDirection = "column";
//         // nav.style.position = "absolute";
//         // nav.style.backgroundColor = "white";
//         // nav.style.top = "40px";
//         // nav.style.right = "10px";
//         // nav.style.backgroundColor = "white";
//         // nav.style.border = "1px solid #ccc";
//         // nav.style.boxShadow = "0px 4px 6px rgba(0, 0, 0, 0.1)";
//         // nav.style.padding = "10px";
//         // nav.style.borderRadius = "5px";
//         // nav.style.zIndex = "1000";
//     }
// function hide()
// {
//     let nav = document.getElementById("newone");
//     nav.style.display = "none";
// }
//scroll function for nav bar
function scrolling()
{
    var navbar=document.querySelector(".nav");
    if(window.scrollY>600)
    {
        navbar.style.position="fixed";
        navbar.style.top="0";
        navbar.classList.add("scrolled");
    }
    else
    {
        navbar.style.position="absolute";
        navbar.style.top="50px";
        navbar.classList.remove("scrolled");
    }
}
//products.html
document.querySelectorAll('.buy-now').forEach(button => {
    button.addEventListener('click', function () {
        let productName = this.getAttribute('data-name');
        let productPrice = this.getAttribute('data-price');
        let productImage = this.getAttribute('data-image');

        fetch('/add_to_cart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: productName,
                price: productPrice,
                image: productImage
            })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message); // Show success message
        })
        .catch(error => console.error('Error:', error));
    });
});

//cart 
document.querySelectorAll('.remove-item').forEach(button => {
    button.addEventListener('click', function () {
        let productName = this.getAttribute('data-name');

        fetch('/remove_from_cart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: productName })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            location.reload(); // Reload cart to reflect changes
        })
        .catch(error => console.error('Error:', error));
    });
});



