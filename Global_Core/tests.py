# import pycurl
# import urllib.parse
# import io
#
# class gwapi():
#
#     def __init__(self):
#         self.login= dict()
#         self.order = dict()
#         self.billing = dict()
#         self.shipping = dict()
#         self.responses = dict()
#
#     def setLogin(self,security_key):
#         self.login['security_key'] = security_key
#
#     def setOrder(self, orderid, orderdescription, tax, shipping, ponumber,ipadress):
#         self.order['orderid'] = orderid;
#         self.order['orderdescription'] = orderdescription
#         self.order['shipping'] = '{0:.2f}'.format(float(shipping))
#         self.order['ipaddress'] = ipadress
#         self.order['tax'] = '{0:.2f}'.format(float(tax))
#         self.order['ponumber'] = ponumber
#
#
#     def setBilling(self,
#             firstname,
#             lastname,
#             company,
#             address1,
#             address2,
#             city,
#             state,
#             zip,
#             country,
#             phone,
#             fax,
#             email,
#             website):
#         self.billing['firstname'] = firstname
#         self.billing['lastname']  = lastname
#         self.billing['company']   = company
#         self.billing['address1']  = address1
#         self.billing['address2']  = address2
#         self.billing['city']      = city
#         self.billing['state']     = state
#         self.billing['zip']       = zip
#         self.billing['country']   = country
#         self.billing['phone']     = phone
#         self.billing['fax']       = fax
#         self.billing['email']     = email
#         self.billing['website']   = website
#
#     def setShipping(self,firstname,
#             lastname,
#             company,
#             address1,
#             address2,
#             city,
#             state,
#             zipcode,
#             country,
#             email):
#         self.shipping['firstname'] = firstname
#         self.shipping['lastname']  = lastname
#         self.shipping['company']   = company
#         self.shipping['address1']  = address1
#         self.shipping['address2']  = address2
#         self.shipping['city']      = city
#         self.shipping['state']     = state
#         self.shipping['zip']       = zipcode
#         self.shipping['country']   = country
#         self.shipping['email']     = email
#
#
#     def doSale(self,amount, ccnumber, ccexp, cvv=''):
#
#         query  = ""
#         # Login Information
#
#         query = query + "security_key=" + urllib.parse.quote(self.login['security_key']) + "&"
#         # Sales Information
#         query += "ccnumber=" + urllib.parse.quote(ccnumber) + "&"
#         query += "ccexp=" + urllib.parse.quote(ccexp) + "&"
#         query += "amount=" + urllib.parse.quote('{0:.2f}'.format(float(amount))) + "&"
#         if (cvv!=''):
#             query += "cvv=" + urllib.parse.quote(cvv) + "&"
#         # Order Information
#         for key,value in self.order.items():
#             query += key +"=" + urllib.parse.quote(str(value)) + "&"
#
#         # Billing Information
#         for key,value in self.billing.items():
#             query += key +"=" + urllib.parse.quote(str(value)) + "&"
#
#         # Shipping Information
#         for key,value in self.shipping.items():
#             query += key +"=" + urllib.parse.quote(str(value)) + "&"
#
#         query += "type=sale"
#         return self.doPost(query)
#
#
#
#     def authorize(self, amount, ccnumber, ccexp, cvv=''):
#         query = ""
#
#         # Login Information
#         query = query + "security_key=" + urllib.parse.quote(self.login['security_key']) + "&"
#
#         # Authorization Information
#         query += "ccnumber=" + urllib.parse.quote(ccnumber) + "&"
#         query += "ccexp=" + urllib.parse.quote(ccexp) + "&"
#         query += "amount=" + urllib.parse.quote('{0:.2f}'.format(float(amount))) + "&"
#         if cvv:
#             query += "cvv=" + urllib.parse.quote(cvv) + "&"
#
#         # Order Information
#         for key, value in self.order.items():
#             query += key + "=" + urllib.parse.quote(str(value)) + "&"
#
#         # Billing Information
#         for key, value in self.billing.items():
#             query += key + "=" + urllib.parse.quote(str(value)) + "&"
#
#         # Shipping Information
#         for key, value in self.shipping.items():
#             query += key + "=" + urllib.parse.quote(str(value)) + "&"
#
#         query += "type=auth"
#         return self.doPost(query)
#
#     def doPost(self,query):
#         responseIO = io.BytesIO()
#         curlObj = pycurl.Curl()
#         curlObj.setopt(curlObj.POST,1)
#         curlObj.setopt(curlObj.CONNECTTIMEOUT,30)
#         curlObj.setopt(curlObj.TIMEOUT,30)
#         curlObj.setopt(curlObj.HEADER,0)
#         curlObj.setopt(curlObj.SSL_VERIFYPEER,0)
#         curlObj.setopt(curlObj.WRITEFUNCTION,responseIO.write);
#
#         curlObj.setopt(curlObj.URL,"https://secure.networkmerchants.com/api/transact.php")
#
#         curlObj.setopt(curlObj.POSTFIELDS,query.encode())
#
#         curlObj.perform()
#
#         data = responseIO.getvalue()
#         temp = urllib.parse.parse_qs(data.decode())
#         for key,value in temp.items():
#             self.responses[key] = value[0]
#         return self.responses['response']
#
# # NOTE: your security_key should replace the one below
# gw = gwapi()
# gw.setLogin("6457Thfj624V5r7WUwc5v6a68Zsd6YEm");
#
# gw.setBilling("John","Smith","Acme, Inc.","123 Main St","Suite 200", "Beverly Hills",
#         "CA","90210","US","555-555-5555","555-555-5556","support@example.com",
#         "www.example.com")
# gw.setShipping("Mary","Smith","na","124 Shipping Main St","Suite Ship", "Beverly Hills",
#         "CA","90210","US","support@example.com")
# gw.setOrder("1234","Big Order",1, 2, "PO1234","65.192.14.10")
#
# r = gw.doSale("5.00","4111111111111111","1212",'999')
# print(gw.responses['response'])
#
#
# if (int(gw.responses['response']) == 1) :
#     print("Approved")
# elif (int(gw.responses['response']) == 2) :
#     print("Declined")
# elif (int(gw.responses['response']) == 3) :
#     print("Error")
