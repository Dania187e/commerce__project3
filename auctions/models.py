from django.contrib.auth.models import AbstractUser
from django.db import models




class User(AbstractUser):
    pass

class Category(models.Model):
    category_name = models.CharField(max_length=50)

    def __str__(self):
       return self.category_name
    

class Bid(models.Model):
    bid=models.FloatField(default=0)
    user= models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="userBid")

    def __str__(self):
        return f"Bid by {self.user.username}: {self.bid}"
    

class Listing(models.Model):
    title=models.CharField(max_length=30)
    description= models.CharField(max_length=300)
    imageUrl= models.CharField(max_length=1000)
    price=models.ForeignKey(Bid, on_delete=models.CASCADE, blank=True, null=True, related_name="bid_price")
    isActive=models.BooleanField(default=True)
    owner=models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    category=models.ForeignKey(Category,on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    watchlist=models.ManyToManyField(User, blank=True, null=True, related_name="listingWatchlist")

    def __str__(self):
       
       return self.title
    
    def update_highest_bid(self, new_bid):
        if self.highest_bid is None or new_bid > self.highest_bid:
            self.highest_bid = new_bid
            self.save()

class Comment(models.Model):
    author=models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True,  related_name="usercomment")
    listing=models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True,  related_name="listingcomment")
    message=models.CharField(max_length=200)

    def __str__(self):
        return f"{self.author} comment on {self.listing}"
    



