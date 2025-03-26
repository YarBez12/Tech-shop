document.addEventListener("DOMContentLoaded", function () {
    let searchInput = document.getElementById("search-input");
    let suggestionsBox = document.getElementById("search-suggestions");
    let searchBtn = document.getElementById("search-btn");
    let searchUrl = document.getElementById("search-suggestions-url").value;
    

    searchInput.addEventListener("input", function () {
        let query = this.value.trim();
        if (query.length === 0) {
            suggestionsBox.style.display = "none";
            return;
        }

        fetch(`${searchUrl}?q=${query}`)
            .then(response => response.json())
            .then(data => {
                suggestionsBox.innerHTML = "";
                let totalResults = data.categories.length + data.products.length;
                if (totalResults > 0) {
                    suggestionsBox.style.display = "block";
                    if (data.categories.length > 0) {
                        // let categoryHeader = document.createElement("li");
                        // categoryHeader.classList.add("list-group-item", "fw-bold", "text-primary");
                        // categoryHeader.textContent = "Categories";
                        // suggestionsBox.appendChild(categoryHeader);

                        data.categories.forEach(category => {
                            let listItem = document.createElement("li");
                            listItem.classList.add("list-group-item");
                            listItem.innerHTML = `<strong>${category.title}</strong>`;
                            // listItem.dataset.slug = category.slug;
                            // listItem.dataset.type = "category";
                            listItem.addEventListener("click", function () {
                                window.location.href = category.url;
                            });
                            suggestionsBox.appendChild(listItem);
                        });
                    }

                    if (data.products.length > 0) {
                        // let productHeader = document.createElement("li");
                        // productHeader.classList.add("list-group-item", "fw-bold", "text-success");
                        // productHeader.textContent = "Products";
                        // suggestionsBox.appendChild(productHeader);

                        data.products.forEach(product => {
                            let listItem = document.createElement("li");
                            listItem.classList.add("list-group-item");
                            listItem.innerHTML = `<strong>${product.title}</strong>`;
                            // listItem.dataset.slug = product.slug;
                            // listItem.dataset.type = "product";
                            listItem.addEventListener("click", function () {
                                window.location.href = product.url;
                            });
                            suggestionsBox.appendChild(listItem);
                        });
                    }
                } else {
                    suggestionsBox.style.display = "none";
                }
            });
    });

    document.addEventListener("click", function (e) {
        if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.style.display = "none";
        }
    });


    searchInput.addEventListener("keypress", function (e) {
        if (e.key === "Enter") {
            searchBtn.click();
        }
    });
});

  