Final Report
App Name: Fashion Seeker

Github Link: https://github.com/janewukk/FashionSeeker

S3 Endpoint: https://s3.amazonaws.com/fashionseeker/index.html

Youtube Link: https://www.youtube.com/watch?v=0dJJB7wFCSI&feature=youtu.be

Team members:
Bowen Tan (bt2484)
Junyue Wu (jw3674)
Jian Song (js5316)
TianChang Cheng (tc2947)

Motivation:
Discount-driven shoppers are dissatisfied with checking promotion emails
Promotion emails contain too much information not needed and users need one-click action for extracting the discount.

Functionality:
- Sign up and Log in: 
A user can sign up for an account using the email address the first time they log in to the app.
User’s favorite websites will be stored in dynamoDB in the backend.
A user needs to log into the Fashion Seeker website to search and see brand’s discount.
- Search a brand:
Input a favorite brand and click the search button, the related brand together with its discount information will be displayed below the searching box.
Once searched, the brand will be automatically added to the user’s favorite brand list.
Display discount information. Once logged in and at least one website has been added, users can click on “display discount” button to display the list of latest discount information of their favorite pages.
- Send email. Once logged in and at least one website has been added, users can click on the “send email” button on the top right corner to send an email to their registered email address with the latest discount information of their favorite websites.

Design:
- Static Webpage Hosting: 
S3 bucket
HTML + javascript + CSS
Authentication: Cognito
- API connecting frontend to backend: 
API Gateway to listen to frontend request via rest API calls and forward the request to the backend to process.
- Backend processing request and connect to the database: 
Lambda Function (serverless)
Generate discount summary by the user and send it back to the frontend.
Search google API and return related website and automatically pick the most relevant one, check whether it is a shopping website, and add it to the user’s favorite website in the dynamoDB.
Generate discount summary per user and send the summary via SES(email service).
- Database Support: 
DynamoDB Design:

User Table: username -> [list of favorite brand url]

Discount Table: brand URL -> {brand name and latest discount}
DynamoDB Update:
Crawl shopping website URL, get the latest discount information
Update the dynamoDB discount table every 30 minutes (automated trigger by CloudWatch event).

Implementation:
API Gateway:
- /GET
Connect to Lambda function (userToListOfWebs), get user’s discounts of the brand websites the user have favorited according to user_name. Display discounts on frontend when the user hit “My Brand Discount” button.
- /POST
Connect to Lambda function (search-discounts-3), get the discounts of the brand website have searched according to user’s input. Display discounts on frontend when the user hit “search” button.
- /PUT
Connect to Lambda function (sendEmailButton), send discounts of brands user have favorited to user’s email. Send email when the user hit “Send Email” button on the frontend.

Lambda Function:
- userToListOfWebs
Called when the user hit ”send email” button on the frontend. The function will connect to the user table and discount table in DynamoDB. First, we retrieve the URLs of the user’s favorite website brands from the user table. Then, we loop the URLs to retrieve each brand’s discounts information from the discount table. Finally, we return the URLs and discounts information and brand name in JSON format back to the frontend.
- search-discounts-3
Called whenever user searches a brand in “search” input text. The function connect to user table and discount table in DynamoDB. The input frontend passed to this lambda function is user_name and user’s input. First, we call Google API to search user’s input on google and get the most relevant brand shopping website URL and name back. Second, we first search the URL in the discount table in DynamoDB, if this website has already existed in DynamoDB, we retrieve the discounts information from the database and return in a JSON format to the frontend. Third, otherwise, if search-in-db of the website missed, we call the getDiscount lambda function with URL as input to script the discounts from the brand’s website and insert discounts into the discount table. And we return the discounts information to the frontend. Finally, we insert this URL as user’s favorite into user table in DynamoDB.
- Testing (which should be called crawler)
Take an input of website URL, crawl the website and get its HTML page. Go through the HTML page and search for keywords such as %off or discount. Remove those discount sentences that are either too short or duplicate. Return the discount as a list including all discount we could found on the page.
- getDiscount
Called when a brand user searched is not recorded in the dynamoDB. After getting it’s the latest discount by crawling the URL of the brand, we do the insertion of the new brand. If we fail to crawl a website, we will return an empty discount list.
- RetrievedDiscountByItself
Basically calling getDiscount for every Url listed in the discount table.
- Send Email Button
Triggered when the user calls the send email button. Take a username and query the dynamoDB for the user’s favorite pages and their latest discount information. Then send an email contains that information to user’s email address.
- Send Email
Send email daily does the same thing as 6 once a day even without the user clicking the button.


DynamoDB:
- Discount table:
Use URL (brand website’s URL) as key to insert and retrieve. Contains attributes of discount (discount information) as a list, name (brand’s title) as a string.
- User table:
Use username (user’s email) as key to insert and retrieve. Contains attributes of URLs (user’s favorite website’s URLs) as a list.


Appendix:
Architecture Diagram
![alt text](/img/architecture.png)

Sample webpage
![alt text](/img/webpage.jpg)

Website

