# -*- coding: utf-8 -*- 

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################  

@auth.requires_login()
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    response.flash = T('Welcome to web2py')
    return dict(message=T('Hello World'))


def user():
    """
    exposes:
    http://..../[app]/default/user/login 
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

@auth.requires_login()
def add_feedback():
    feedback = SQLFORM(db.feedback, fields=(['category', 'header', 'message','status']))
    if feedback.accepts(request.vars, session):
        session.flash = "Feedback Accepted"
        redirect(URL(r=request))
    return dict(feedback=feedback)
    
@auth.requires_login()
def add_response():
    feedback_id = request.args(0)
    r = db(db.feedback.id == feedback_id).select(db.feedback.ALL)
    responses = db(db.response.feedback_id == feedback_id).select(db.response.ALL, orderby = db.response.id)
    print db.feedback.message
    form = SQLFORM.factory(Field('comment', 'text', requires=IS_NOT_EMPTY()))
    if form.accepts(request.vars, session):
        db.response.insert(feedback_id=feedback_id, comment=form.vars.comment)
        session.flash = "Comment Added"
        redirect(URL(r=request, c='default', f='add_response', args=[feedback_id]))    
    return dict(form=form, feedback=r[0], responses=responses)
    
@auth.requires_login()
def homepage():
    form = SQLFORM.factory(
        Field('search', 'string'), submit_button="Search")
    searchtext = ''
    if form.accepts(request.vars, session):
        searchtext = form.vars.search
    cm_count = db.response.id.count()
    searchtext = searchtext.lower()   
    posts = ''
    if form.vars.search and len(form.vars.search) > 0:
        posts = db((db.auth_user.id == db.feedback.user_id) & ((db.feedback.header.lower().contains(searchtext)) | (db.feedback.message.lower().contains(searchtext)))).select(db.feedback.ALL, db.auth_user.first_name, db.auth_user.last_name, cm_count, orderby = ~db.feedback.created_on, groupby = db.feedback.id | db.feedback.user_id | db.feedback.status | db.feedback.category | db.feedback.header | db.feedback.message | db.feedback.created_on | db.feedback.vote_count | db.auth_user.first_name | db.auth_user.last_name, left = db.response.on(db.feedback.id == db.response.feedback_id))
    else:
        posts = db(db.auth_user.id == db.feedback.user_id).select(db.feedback.ALL, db.auth_user.first_name, db.auth_user.last_name, cm_count, orderby = ~db.feedback.created_on, groupby = db.feedback.id | db.feedback.user_id | db.feedback.status | db.feedback.category | db.feedback.header | db.feedback.message | db.feedback.created_on | db.feedback.vote_count | db.auth_user.first_name | db.auth_user.last_name, left = db.response.on(db.feedback.id == db.response.feedback_id))
    
            
    print db._lastsql
    return dict(post=posts, form=form)
    
def vote():
    feedback = db.feedback[request.vars.id]
    if request.vars.key == "up":
        c = feedback.vote_count + 1
    else:
        c = feedback.vote_count - 1    
    feedback.update_record(vote_count = c)
    redirect(URL(r=request, c='default', f='homepage'))
    return str(c)
