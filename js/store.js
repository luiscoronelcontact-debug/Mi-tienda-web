🤖 Qwen está procesando tu solicitud para CELL ZONE...

```javascript
document.addEventListener('DOMContentLoaded', () => {
    const products = [
        { id: 1, name: 'iPhone 13', description: 'Latest iPhone model with A15 Bionic chip.', priceUsd: 21.60, priceArs: 25920},
        { id: 2, name: 'Samsung Galaxy S21', description: 'Flagship Samsung phone with Exynos 2100.', priceUsd: 18.99, priceArs: 22788},
        { id: 3, name: 'Google Pixel 6', description: 'Google\'s latest flagship with Tensor chip.', priceUsd: 24.99, priceArs:29988 }
    ];

    function renderProducts() {
        const productsContainer = document.getElementById('products-container');
        productsContainer.innerHTML = '';

        products.forEach(product => {
            const productCard = document.createElement('div');
            productCard.className = 'bg-white rounded-lg shadow-md overflow-hidden mb-6';

            productCard.innerHTML = `
                <img src="images/${product.id}.jpg" alt="${product.name}" class="w-full h-48 object-cover">
                <div class="p-4">
                    <h3 class="text-lg font-bold">${product.name}</h3>
                    <p class="text-gray-500">${product.description}</p>
                    <div class="mt-4">
                        <span class="text-green-500 text-xl">${product.priceUsd.toFixed(2)} USD</span><br>
                        <span class="text-gray-400 text-sm">${product.priceArs.toLocaleString()} ARS</span>
                    </div>
                    <button onclick="openModal(${product.id})" class="mt-4 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4rounded">Ver más</button>
                </div>
            `;

            productsContainer.appendChild(productCard);
        });
    }

    function openModal(productId) {
        const product = products.find(p => p.id === productId);
        const modal = document.getElementById('product-modal');
        modal.style.display = 'block';

        modal.innerHTML = `
            <div class="bg-white rounded-lg shadow-lg p-6 relative">
                <button onclick="closeModal()" class="absolute top-0 right-0 mt-4 mr-4 text-gray-500 hover:text-gray-700 focus:outline-none">
                    <svg class="h-6 w-6 fill-current" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2424"><path d="M16.192 6.344L11.949 10.586 7.707 6.344 6.293 7.759 10.535 12 6.293 16.241 7.707 17.656 11.949 13.414 16.192 17.656 17.607 16.241 13.365 12 17.607 7.759z"/></svg>
                </button>
                <img src="images/${product.id}.jpg" alt="${product.name}" class="w-full h-48 object-cover mb-4">
                <h3 class="text-lg font-bold">${product.name}</h3>
                <p class="text-gray-500">${product.description}</p>
                <div class="mt-4">
                    <span class="text-green-500 text-xl">${product.priceUsd.toFixed(2)} USD</span><br>
                    <span class="text-gray-400 text-sm">${product.priceArs.toLocaleString()} ARS</span>
                </div>
            </div>
        `;
    }

    function closeModal() {
        const modal = document.getElementById('product-modal');
        modal.style.display = 'none';
    }

    renderProducts();
});
```
