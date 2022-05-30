## How to use TD Ameritrade API?

- register and log in https://developer.tdameritrade.com/
- create an App under "My Apps" (at most one app per developer account)
    - set app name
    - set Callback URL to: http://127.0.0.1:8080 (https doesn't work)
    - write down Consumer Key (API key)
- go to https://auth.tdameritrade.com/auth?response\_type=code&redirect\_uri=http%3A%2F%2F127.0.0.1%3A8080&client\_id={API key}%40AMER.OAUTHAP
- log in TD Ameritrade trading account (different from API account)
- page will be forwarded to https://127.0.0.1:8080/?code=XXX
- write down the code XXX from the last step and urldecode it
- go to https://developer.tdameritrade.com/authentication/apis/post/token-0 and fill the following fields:
  - grant\_type: authorization\_code
  - access\_type: offline
  - code: previous urldecoded code
  - client\_id: API key
  - redirect\_uri: http://127.0.0.1:8080
- click 'send' button and get json response as the token file

## Reference:

- https://developer.tdameritrade.com/content/getting-started
- https://developer.tdameritrade.com/content/authentication-faq
- https://medium.com/swlh/printing-money-with-td-ameritrades-api-a5cccf6a538c
