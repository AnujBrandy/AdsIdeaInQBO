# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
import datetime
from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.webdriver.common.keys import Keys
import time

complete_ad=""

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Welcome to web2py!")
    #return dict(message=T('Hello World'))
    redirect(URL('home'))


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login()
def home():
    list_of_ads=db(db.ads.user_id==auth.user_id).select(db.ads.ALL)
    return dict(list_of_ads=list_of_ads)

def create_company():
    form=SQLFORM.factory(
            Field('company_name','string',notnull=True)
            )
    if form.process().accepted:
        db.company.insert(company_name=request.vars.company_name,user_id=auth.user_id)
        redirect(URL('home'))
    return dict(form=form)


def create_ads():
    dict_of_companies=db(db.company.user_id==auth.user_id).select(db.company.ALL)
    list_of_companies=[]
    for i in dict_of_companies:
        list_of_companies.append(i.company_name)
    form=SQLFORM.factory(
        Field('company_name','string',requires=IS_IN_SET(list_of_companies)),
        Field('company_url','string',notnull=True,requires=IS_URL()),
        Field('ads_content','text'),
        Field('ad_cost','integer',default=0)
    )
    if form.process().accepted:
        companyid=db((db.company.company_name==request.vars.company_name) & (db.company.user_id==auth.user_id)).select(db.company.id)[0]
        print companyid
        db.ads.insert(company_id=companyid,user_id=auth.user_id,company_url=request.vars.company_url,
            ads_content=request.vars.ads_content,ad_cost=request.vars.ad_cost)
        redirect(URL('home'))
    return dict(form=form)

def page_is_loaded(driver):
    return driver.find_element_by_tag_name("body") != None

def select_ad():
    list_of_ads=db((db.ads.id>0) & (db.ads.user_id!=auth.user_id)).select(db.ads.ALL)
    return dict(list_of_ads=list_of_ads)

def adding_ads():
    ad_id1=db(db.user_transaction.user_id_2==auth.user_id).select(db.user_transaction.user_id_1)[0]
    ad_description=db(db.ads.user_id==ad_id1.user_id_1).select(db.ads.company_id,db.ads.company_url,db.ads.ads_content,db.ads.ad_cost)
    company_n=db(db.company.id==ad_description[0]['company_id']).select(db.company.company_name)[0]
    global complete_ad
    complete_ad="""
    Company Name  :  """ + company_n.company_name + """
    Ads  :  """ + ad_description[0]['ads_content'] + """
    Description  :   """ + ad_description[0]['company_url']
    print complete_ad
    emailid=request.args(0)
    password=request.args(1)
    driver = webdriver.Firefox()
    driver.get("https://qbo.intuit.com")    
    wait = ui.WebDriverWait(driver, 10000)
    wait.until(page_is_loaded)
    email_field = driver.find_element_by_id("login")
    email_field.send_keys(emailid)#"shashank.agarwal94a@gmail.com")  
    password_field = driver.find_element_by_id("password")
    password_field.send_keys(password)#"password123")
    password_field.send_keys(Keys.RETURN)
    time.sleep(10)
    driver.get("https://sg.qbo.intuit.com/app/formstyles")
    wait = ui.WebDriverWait(driver, 10000)
    wait.until(page_is_loaded)
    time.sleep(5)
    driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div[2]/div[2]/div[3]/div/div[1]/table/tr').click()
    time.sleep(5)
    wait.until(page_is_loaded)
    wait = ui.WebDriverWait(driver, 10000)
    wait.until(page_is_loaded)
    time.sleep(5)
    driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/div/div[1]/div[5]/a').click()
    ads=driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/div/div[2]/div[2]/div[2]/div/div/div[2]/textarea')
    ads.send_keys(complete_ad)
    driver.find_element_by_xpath('/html/body/div/div[2]/div/div/footer/div/div[2]/button[2]').click()
    wait = ui.WebDriverWait(driver, 10000)
    wait.until(page_is_loaded)
    time.sleep(5)
    redirect(URL('home'))

    
def login_qbo():
    form=SQLFORM.factory(
        Field('email_id','string'),
        Field('password','password')
        )
    if form.process().accepted:
        arguments=[]
        arguments.append(request.vars.email_id)
        arguments.append(request.vars.password)
        print request.vars
        redirect(URL(adding_ads,args=arguments))
    return dict(form=form)



def save_ads():
    ad_id=int(request.vars.ads)
    if_present=db(db.user_transaction.user_id_2==auth.user_id).select(db.user_transaction.ALL)
    dictionary1=db(db.ads.id==ad_id).select(db.ads.user_id,db.ads.ad_cost)
    if if_present:
        db(db.user_transaction.user_id_2==auth.user_id).update(user_id_1=dictionary1[0].user_id,amount=dictionary1[0].ad_cost)
    else:
        db.user_transaction.insert(user_id_1=dictionary1[0].user_id,user_id_2=auth.user_id,amount=dictionary1[0].ad_cost)
    redirect(URL('home'))



def see_your_ad():
    ad_id1=db(db.user_transaction.user_id_2==auth.user_id).select(db.user_transaction.user_id_1)[0]
    ad_description=db(db.ads.user_id==ad_id1.user_id_1).select(db.ads.company_id,db.ads.company_url,db.ads.ads_content,db.ads.ad_cost)
    company_n=db(db.company.id==ad_description[0]['company_id']).select(db.company.company_name)[0]
    global complete_ad
    return dict(company_name=company_n,ad_content=ad_description[0]['ads_content'],company_url=ad_description[0]['company_url'])








