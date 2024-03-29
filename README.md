
# DCA Bot via Coinbase REST API

A script to run automated deposits and limit buys via CB Market API securely. This method saves you roughly 7-10x in fees vs the standard Coinbase recurring purchase tool. 

***IMPORTANT:
This script connects and withdraws from your real bank accounts! I am not responsible for any mistakes/losses incurred as a result of using this. 
- Make sure to do test transactions of small values before letting this run on a schedule.
- Be sure to not expose any API Keys or env variables. I am using AWS Parameter Store to securely store mine.


## AWS Suite - Free Tier

To deploy this project, you will need an AWS free tier account. We will be using the AWS suite of tools (Lambda/Systems Manager/EventBridge) to set up scheduling/automation of this dollar cost averaging script. 


## Deployment
1.  In AWS, search for "Lambda"
2.  Create a new function for each .py file in this repo. Select "Python 3.9" for your runtime and leave all other settings as is. 
-   one function is for your deposit via bank and another is for setting your limit buys 
3.  Navigate to Additional Resources -> Layers 
4.  Create layer -> upload the .zip file 
5.  Go back to your "cb_deposit" Lambda and click Add Layer
6.  Specify ARN -> copy/paste the ARN of the layer you just uploaded


## Environment Variables

To run this project, you will need to add the following environment variables to your Systems Manager Parameter Store 
1.  Navigate to Systems Manager > Application Management > Parameter Store
2.  Copy and paste these from your Coinbase API Keys. I made 2 separate API keys (for deposit/buy) with different permissions using principle of least privilege.

Create Parameter > 

`cb_buy_apiKey`	
SecureString	

`cb_buy_apiSecret`	
SecureString	

`cb_deposit_apiSecret`	
SecureString	

`cb_deposit_apiKey`	
SecureString	

To get these values you will need to comment in list_payment_methods() and invoke your deposit lambda for the first time. After invoking, check the log to see which accounts are connected. You can comment the function back out after. 

`cb_deposit_depositId`	
String	

`cb_deposit_paymentMethod`
String



## Scheduling
1.  In AWS, search for "Event Bridge"
2.  In the left-hand menu, navigate to "Scheduler" > "Schedules"
3.  Click "Create Schedule" - we will be making 2 schedules: 1 for the recurring deposit, 1 for the recurring limit buy orders.
4.  Select a name and your desired time frame. I used rate-based (3 days) as it is more straight forward to use than cron based. Click "Next"
5.  Select Target > Templated Target > "Invoke Lambda" then select the corresponding Lambda function you created in the previous section from the dropdown  
6.  Disable the retry policy & dead-letter queue.
7.  Under permissions, create a new role if this is your first time doing this. If you are doing this for your second lambda you can reused the previously created role. 
8.  Create schedule and you should be done! You can test it out :)

## Modifying order amounts/tickers
Within your buy Lambda, just modify the order_sizes object with the corresponding ticker and amount you want to purchase on a recurring basis. You can see a list of all available tickers in the Coinbase docs: https://docs.cloud.coinbase.com/exchange/reference/exchangerestapi_getproducts