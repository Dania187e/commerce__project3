from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Category, Listing, Comment, Bid


def listing(request, id):
    listingData =Listing.objects.get( pk=id)
    isListingInWatchlist=request.user in listingData.watchlist.all()
    allComments=Comment.objects.filter(listing=listingData)
    isOwner=listingData.owner == request.user

    return render(request, "auctions/listing.html",{
        "listing":listingData,
        "isListingInWatchlist": isListingInWatchlist,
        "allComments": allComments,
        "isOwner": isOwner

    })



def closeAuction(request,id):
    listingData=Listing.objects.get(pk=id)
    listingData.isActive
    listingData.save()
    isListingInWatchlist=request.user in listingData.watchlist.all()
    allComments=Comment.objects.filter(listing=listingData)
    isOwner= request.user.username == listingData.owner.username

    return render(request, "auctions/listing.html",{
        "listing":listingData,
        "isListingInWatchlist": isListingInWatchlist,
        "allComments": allComments,
        "isOwner": isOwner,
        "updated": True,
        "message": "the auction is closed."

    } )
# adding bid tp products
from django.core.exceptions import ValidationError

def addBid(request, id):
    if request.method ==  "POST":
        listingData=Listing.objects.get(pk=id)
        newBid = request.POST.get("newBid")

        highest_bid = None
        if listingData.price is not None:
            highest_bid = listingData.price.bid
        # count the highest bid without get under zero
        if newBid is not None and int(newBid) > 10:
            try:
                updatedBid=Bid(user=request.user, bid=int(newBid))
                updatedBid.save()
            except ValidationError as e:
                pass

            if listingData.price is None:
                listingData.price = updatedBid
                listingData.price.save()
            else:
                listingData.price.bid = int(newBid)
                listingData.price.save()
                

            message = "Bid was updated successfully"
            updated = True
        else:
            message = "Bid update failed, enter a higher bid."
            updated = False

        isOwner = listingData.owner is not None and request.user.username == listingData.owner.username
        isListingInWatchlist = request.user in listingData.watchlist.all()
        allComments = Comment.objects.filter(listing=listingData)

        return render(request, "auctions/listing.html", {
            "listing": listingData,
            "message": message,
            "updated": updated,
            "isListingInWatchlist": isListingInWatchlist,
            "allComments": allComments,
            "isOwner": isOwner,
            "highest_bid": highest_bid,
        })
    else:
        return HttpResponseRedirect(reverse("index"))


       
# comment about product       
def addComment(request, id):
    currentUser=request.user
    listingData=Listing.objects.get(pk=id)
    message=request.POST['newComment']
    
    newComment=Comment(
        author=currentUser,
        listing=listingData,
        message=message

    )
    newComment.save() #save comments in database
    return HttpResponseRedirect(reverse("listing",args=(id, )))


def displayWatchlist(request):
    currentUser=request.user
    listings =currentUser.listingWatchlist.all()
    return render(request, "auctions/watchlist.html",{
        "listings": listings
    })

# remove and add in watchlist
def addWatchlist(request, id):
    listingData=Listing.objects.get(pk=id)
    currentUser=request.user
    listingData.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing",args=(id, )))



def removeWatchlist(request, id):
    listingData=Listing.objects.get(pk=id)
    currentUser=request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing",args=(id, )))




def index(request):
    activeListings=Listing.objects.filter(isActive=True)
    all_categories= Category.objects.all()
    return render(request, "auctions/index.html",{
        "listings": activeListings,
        "categories": all_categories 
    })
# category of product 
def displayCategory(request):
    category_data= None
    if request.method=="POST":
        categoryFromForm=request.POST['Category']
        if categoryFromForm:
            category_data=Category.objects.get(category_name=categoryFromForm)
            activeListings=Listing.objects.filter(isActive=True, category=category_data)
        else:
            activeListings=Listing.objects.filter(isActive=True)
        all_categories= Category.objects.all()
        return render(request, "auctions/index.html",{
            "listings": activeListings,
            "categories": all_categories 
        })
    return render(request,"auctions/displayCategory.html")
    
   
  


def CreateListing(request):
    if request.method == "GET":
        all_categories= Category.objects.all()
        return render(request, "auctions/create.html",{
            "categories":all_categories

        })
    else:

        #get the data from the form 
        title=request.POST["title"]
        description=request.POST["description"]
        imageurl=request.POST["imageurl"]
        price=request.POST["price"]
        category_name=request.POST["Category"]
        #who is the user 
        current_user= request.user
        #get all content about the category
        try:
            category_data=Category.objects.get(category_name=category_name)
        except Category.DoesNotExist:
            #handle the case when the category does not exist
            return render(request,"auctions/create.html",{
                "categories":Category.objects.all(),
                "error_message":"invalid category."
            })
        # create object of bid:
        bid=Bid(bid=float(price), user=current_user)
        bid.save()
        #create a new listing object
        new_Listing=Listing(

            title=title,
            description=description,
            imageUrl=imageurl,
            price=bid,
            category=category_data,
            owner=current_user
        )
        #insert the object in the database
        new_Listing.save()
        #redircect to index page
        return HttpResponseRedirect(reverse(index))
    

  



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
