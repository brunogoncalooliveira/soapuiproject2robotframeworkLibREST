# soapuiproject2robotframeworkLibREST

I made this script to convert a soapui REST project to a robot framework format (text). REST invocations use Lib RESTintance.
This script is a version 0.1 (if you use it, probably it won't work!).

Use it like this:

**python soapui_to_robot.py soapuiproject.xml testfile.robot**

```
*** Settings ***
Library       REST    https://site.apixyz.com/  ssl_verify=false

*** Variables ***
${default-TPP-Transaction-ID}     32431241324
${default-TPP-Certificate}        ggfgsfdgsfdgsf==
${default-TPP-Request-ID}         AAAVVVCCC1234567896f35c77eac1381d9


*** Keywords ***

SIBS Addon ASPSP List - availableAspspGet
  [Arguments]  ${TPP-Transaction-ID}=${default-TPP-Transaction-ID}
  ...          ${TPP-Certificate}=${default-TPP-Certificate}
  ...          ${TPP-Request-ID}=${default-TPP-Request-ID}
  Set Headers  { "TPP-Transaction-ID": "${TPP-Transaction-ID}"}
  Set Headers  { "TPP-Certificate": "${TPP-Certificate}"}
  Set Headers  { "TPP-Request-ID": "${TPP-Request-ID}"}
  GET  /v1/getclient
  ```
