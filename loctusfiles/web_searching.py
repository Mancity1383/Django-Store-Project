from random import randint,choice
from locust import HttpUser,task,between

carts_id = []

class WebsiteUser(HttpUser):
    wait_time = between(1,4)


    @task(3)
    def view_all_products(self):
        collection_id = randint(2,6)
        self.client.get(
            f'/store/products/?collection_id={collection_id}',
            name='/store/products/')

    @task(4)  
    def view_product(self):
        product_id = randint(1,1000)
        self.client.get(
            f'/store/products/{product_id}/',
            name ='/store/products/:id')

    @task(2)
    def add_to_cart(self):
        response = self.client.post(f'/store/carts/')
        result = response.json()
        cart_id = result['id']
        carts_id.append(cart_id)
        product_id = randint(1,10)
        self.client.post(f'/store/carts/{cart_id}/items/',
                         name = '/store/carts/items',
                         json={
                             'product':product_id,
                             'quantity':1
                         })
        
    @task(2)  
    def delete_cart(self):
        try:
            cart_id = choice(carts_id)
            if cart_id is not None:
                carts_id.remove(cart_id)
                self.client.delete(f'/store/carts/{cart_id}/',name='/store/carts/:id')
        except:
            pass

        
        
    @task(1)
    def create_order(self):
        try:
            cart_id = choice(carts_id)
            if cart_id is not None:
                carts_id.remove(cart_id)
                self.client.post(f'/store/orders/',name='/store/orders',json={'cart_id':cart_id})
        except:
            pass
        

    def on_start(self):
        response = self.client.post("/auth/jwt/create/", json={
            "username": "supernova",
            "password": "Ali@1383"
        })
        self.token = response.json()["access"]
        self.client.headers = {
            "Authorization": f"JWT {self.token}"
        }
