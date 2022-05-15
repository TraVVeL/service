if (document.getElementById('hearderSlide')) {
    $('#hearderSlide').multislider();
    $('#hearderSlide').multislider('pause');
}


function closeCart() {
    $('.producstOnCart').addClass('hide-animation');
    setTimeout(function(){
    const cart = document.querySelector('.producstOnCart');
    cart.classList.toggle('hide');
    },500)
    $('.overlay').addClass('hide');
}


const openShopCart = document.querySelector('.shoppingCartButton');
openShopCart.addEventListener('click', () => {
    const cart = document.querySelector('.producstOnCart');
    cart.classList.toggle('hide');
    $('.producstOnCart').removeClass('hide-animation');
        $('.overlay').removeClass('hide');
});




const closeShopCart = document.querySelector('#closeButton');
const overlay = document.querySelector('.overlay');
closeShopCart.addEventListener('click', closeCart);
overlay.addEventListener('click', closeCart);




let productsInCart = JSON.parse(localStorage.getItem('shoppingCart'));
if(!productsInCart){
    productsInCart = [];
}
const parentElement = document.querySelector('#buyItems');
const cartSumPrice = document.querySelector('#sum-prices');
const quantityItem = document.querySelector('#quantity');
const products = document.querySelectorAll('.el-container');
console.log(productsInCart)

const countTheSumPrice = function () 
    {
        let sum = 0;
        productsInCart.forEach(item => {
            sum += item.final_cost;
        });
        return sum;
    }

const quantityTheItem = function ()
     {
         let quantity = 0;
         productsInCart.forEach(item => {
             quantity = productsInCart.length;
         });
        return quantity;
     }

const updateShoppingCartHTML = function () {  // 3
    localStorage.setItem('shoppingCart', JSON.stringify(productsInCart));

    if (productsInCart.length > 0) {

        let result = productsInCart.map(product => {
            return `
                <div class="buyItem">
                    <a class="el-img" href="${product.product_url}"><img class="el-img" src="${product.product_img}" alt=""></a>
                    <div>
                        <a class="el-modal-name" href="${product.product_url}">${product.product_name}</a>
                                
                        <div class="btn-content">
                            <button class="button-minus el-circle" data-id=${product.product_id}>
                                <div class="button-minus figure-minus" data-id=${product.product_id}></div>
                            </button>

                            <span class="countOfProduct">${product.product_count}</span>

                            <button class="button-plus el-circle" data-id=${product.product_id}>
                                <div class="button-plus figure-plus" data-id=${product.product_id}></div>
                            </button>
                        </div>
                        <p class="el-modal-price">${product.final_cost} р.</p>
                        
                        <button class="button-delete el-circle" data-id=${product.product_id}>
                            <div class="button-delete figure-delete" data-id=${product.product_id}></div>
                        </button>

                    </div>
                </div>`
        });
        parentElement.innerHTML = result.join('');
        document.querySelector('.checkout').classList.remove('hidden');
        document.querySelector('.priceCheckout').classList.remove('hidden');
        document.querySelector('.quantity').classList.remove('hidden');
        document.querySelector('.user-agreement').classList.remove('hidden');
        document.querySelector('.modal-content.product').classList.remove('hidden');
        cartSumPrice.innerHTML = "Итого: " + countTheSumPrice() + " р.";
        quantityItem.innerHTML = quantityTheItem();


    }

    else {
        document.querySelector('.checkout').classList.add('hidden');
        document.querySelector('.priceCheckout').classList.add('hidden');
        document.querySelector('.quantity').classList.add('hidden');
        document.querySelector('.user-agreement').classList.add('hidden');
        document.querySelector('.modal-content.product').classList.add('hidden');
        parentElement.innerHTML = '<h4 class="empty">Упс, похоже, что ваша корзина пуста</h4>';
        cartSumPrice.innerHTML = '';
        quantityItem.innerHTML = '';
    }
}

function updateProductsInCart(product) { // 2
    for (let i = 0; i < productsInCart.length; i++) {
        if (productsInCart[i].product_id == product.product_id) {
            productsInCart[i].product_count += 1;
            productsInCart[i].final_cost = productsInCart[i].product_price * productsInCart[i].product_count;

            return;
        }
    }
    console.log(productsInCart)
    productsInCart.push(product);
}

products.forEach(item => {   // 1
    item.addEventListener('click', (e) => {
        if (e.target.classList.contains('addToCart')) {
            const productID = e.target.dataset.productId;
            const productName = item.querySelector('.url_name').innerHTML;
            const productPrice = item.querySelector('.priceValue').innerHTML;
            const productUrl = item.querySelector('.url_name').href;
            const productImg = item.querySelector('.el-img-front').src;
            const user_id = item.querySelector('#user_id').value;
            let product = {
                product_name: productName,
                product_id: productID,
                product_count: 1,
                final_cost: +productPrice,
                product_price: +productPrice,
                product_url: productUrl, 
                product_img: productImg,
                user_id: user_id
            }
            updateProductsInCart(product);
            updateShoppingCartHTML();
        }
    });
});

parentElement.addEventListener('click', (e) => { // Last
    const isPlusButton = e.target.classList.contains('button-plus');
    const isMinusButton = e.target.classList.contains('button-minus');
    const isDeleteButton = e.target.classList.contains('button-delete');
    if (isPlusButton || isMinusButton || isDeleteButton) {
        for (let i = 0; i < productsInCart.length; i++) {
            if (productsInCart[i].product_id == e.target.dataset.id) {
                if (isPlusButton) {
                    productsInCart[i].product_count += 1
                }
                if (isDeleteButton) {
                    productsInCart[i].product_count = 0
                }
                else if (isMinusButton) {
                    productsInCart[i].product_count -= 1
                }
                productsInCart[i].final_cost = productsInCart[i].product_price * productsInCart[i].product_count;

            }
            if (productsInCart[i].product_count <= 0) {
                productsInCart.splice(i, 1);
            }
        }
        updateShoppingCartHTML();
    }
});

updateShoppingCartHTML();



// fetch all product data from cart
$(document).ready(function() {
    for (let i = 0; i < productsInCart.length; i++) {

        $('#order_form').on('submit', function(event) {
            $.ajax({
                async: false,
                dataType : "json",
                data : productsInCart[i],
                type : 'POST',
                url : '/user_purchase'

            })
            event.preventDefault();
        });

    }
});

// fetch all user data from cart
$(document).ready(function() {
    $('#order_form').on('submit', function(event) {
        $.ajax({
            data : {
                name : $('#name').val(),
                phone : $('#phone').val(),
                mail : $('#mail').val(),
                secondary_name : $('#secondary_name').val(),
                secondary_phone : $('#secondary_phone').val(),
                city : $('#city').val(),
                street : $('#street').val(),
                building_address : $('#building_address').val(),
                entrance : $('#entrance').val(),
                floor : $('#floor').val(),
                apartment : $('#apartment').val(),
                deliver : $('#deliver').val(),
                deliver_time : $('#deliver_time').val(),
                note : $('#note').val(),
                user_id : $('#user_id').val()
            },
            type : 'POST',
            url : '/user_purchase'
        })
        .done(function(data) {
                $('#order_alert').text(data.content).show();
                let order_alert = $('#order_alert');
                order_alert.attr('class', data.category);
        });
        event.preventDefault();


    });
});
