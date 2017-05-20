/**
 * Created by Lenny on 4/17/2017.
 */
const shop = [
    {
        name: "Steak Tacos",
        price: 2.25 ,
        quantity: 0
    },
    {
        name: "Chicken Tacos",
        price: 2.25,
        quantity: 0
    },
    {
        name: "Chorizo Tacos, (Mexican Sausage)",
        price: 2.25,
        quantity: 0
    },
    {
        name: "Cecina Tacos, (Jerky Style Beef)",
        price: 2.25,
        quantity: 0
    },
    {
        name: "Carnitas Tacos, (Deep Fried Pork)",
        price: 2.25,
        quantity: 0
    },
    {
        name: "Tacos de Lengua, (Beef Tongue)",
        price: 2.25,
        quantity: 0
    },
    {
        name: "Torta de Bistec, (Steak Sandwiches)",
        price: 5.50,
        quantity: 0
    },
    {
        name: "Torta de Chorizo, (Mexican Sausage)",
        price: 5.50,
        quantity: 0
    },
    {
        name: "Torta de Cecina, (Deep Fried Pork)",
        price: 5.50,
        quantity: 0
    },
    {
        name: "Torta de Queso Blanco, (Fresh White Cheese)",
        price: 5.50,
        quantity: 0
    },
    {
        name: "Torta de Pollo",
        price: 5.50,
        quantity: 0
    },
    {
        name: "Torta de Jamon, (Ham sandwich)",
        price: 5.50,
        quantity: 0
    },
    {
        name: "Torta de Carne Enchilda, (Spicy Pork)",
        price: 5.50,
        quantity: 0
    }
];

const vm = new Vue({
    el: "#app",
    data: {
        items: [],
        shop: shop,
        showCart: false,
        verified: false
    },
    computed: {
        total() {
            var total = 0;
            for(var i = 0; i < this.items.length; i++) {
                total += this.items[i].price;
            }
            return total;
        }
    },
    methods: {
        addToCart(item) {
            item.quantity += 1;
            this.items.push(item);
        },
        removeFromCart(item) {
            item.quantity -= 1;
            this.items.splice(this.items.indexOf(item), 1);
        }
    }
});