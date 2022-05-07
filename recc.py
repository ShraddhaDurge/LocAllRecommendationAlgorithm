import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask
from flask_restful import Resource, Api, reqparse
import threading
import time
from flask import request


# In[18]:


lock=threading.Lock()
Recommendation_list = []
def recommend_products_to_user(user_id_given):
    global Recommendation_list

    ratings = pd.read_csv("LocAllRated.csv")
    #ratings = ratings.fillna(0)
    ratings.head()

    user_ratings = ratings.pivot_table(index=['UserId'],columns=['ProductId'],values='Rating')
    user_ratings.head()

    ###
    user_ratings = user_ratings.dropna(thresh=1,axis=1).fillna(0)
    user_ratings.head()

    ###
    user_liked = []
    if user_id_given in user_ratings.index :
        user_liked = user_ratings.loc[user_id_given, :].values.flatten().tolist()
        s = pd.Series(user_liked)
        arr = np.array(user_liked)


        out_tpl = np.nonzero(arr)
        #print ("Indices of non zero elements : ", out_tpl)

        user_liked_list = []

        for i in out_tpl:
            user_liked_list= list(zip(i+1,arr[i]))

        # calling .nonzero() method
        #result = s.nonzero()

        # display
        fun_user = user_liked_list
        #print(fun_user)

        ###
        item_similarity_df = user_ratings.corr(method='pearson')
        item_similarity_df.head(100)

        ####
        def get_similar(prod_id,rating):
                similar_ratings = item_similarity_df[prod_id]*(rating-2.5)
                similar_ratings = similar_ratings.sort_values(ascending=False)
                #print(type(similar_ratings))
                return similar_ratings

        ###
        similar_prod_id = pd.DataFrame()

        for prod_id,rating in fun_user:
            similar_prod_id = similar_prod_id.append(get_similar(prod_id,rating),ignore_index = True)

        similar_prod_id.head(10)

    ###
        R_list = similar_prod_id.sum().sort_values(ascending=False).head(20)

    else :
       df2 = user_ratings.sum(axis=0).sort_values(ascending=False).head(20)
       R_list = df2

    res = []
    for x in R_list.iteritems():
        res.append(int(x[0]))

    # lock.acquire()
    # # Recommendation_list = list(similar_prod_id.sum().sort_values(ascending=False).head(10))
    # Recommendation_list = res
    # lock.release()
    print(res)
    return res

# In[19]:


def Updated_rating_data():
    while True:
        recommend_products_to_user(1)
        time.sleep(10000) #update will happen after the LocallRated dataset is updated/new entry of user rating is added
#
# def Updated_rating_data(userId):
#     recommend_products_to_user(userId)


# In[20]:


class Service(Resource):
     def get(self):
        global Recommendation_list
        userId = request.args.get('userid', default = 1, type = int)

        response ={}
        response["productList"] = recommend_products_to_user(userId)
    
        return response

class test(Resource):
    def get(self):
        return "testing"


# In[21]:


app = Flask(__name__)
api = Api(app)


# In[22]:


api.add_resource(Service, '/recommendation')

if __name__ == '__main__':
    print("Server is loading.....")
    # recommend_products_to_user(1)
    print("Server is listening")
    # t1 = threading.Thread(target=recommend_products_to_user(1), args=())
    # t1.start()
    app.run()  # run our Flask app





# In[ ]:





# In[ ]: