#!/usr/bin/env python3

"""Controllers for the project."""

__version__ = '1.0.0'
__author__ = 'hharutyunyan'
__copyright__ = 'Copyright 2018, hharutyunyan'
__license__ = 'All Rights Reserved'
__maintainer__ = 'hharutyunyan'
__status__ = "Production"

from flask import Blueprint, render_template, request, session, redirect, \
    url_for, g
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name

from app.models.users import Users, req_user_login
from app.models.issues import Issues
from app.models.projects import Projects
from app.models.revisions import Revisions
from app.models.issue_comments import Issue_comments

from app import db

routes = Blueprint('routes', __name__, )


@routes.route('/', methods=['GET', 'POST'])
@req_user_login()
def home():
    """Render home page."""
    counts = {
        'projects': Projects().select(
            'owner=%(user_id)s', {'user_id': g.user.id}
        ).rowcount,
        'contributions': Revisions().select(
            'contributor_id=%(user_id)s', {'user_id': g.user.id}
        ).rowcount
    }

    top_projects = Projects().get_top_projects(g.user.id)
    return render_template('home.html', counts=counts,
                           top_projects=top_projects)


@routes.route('/login/', methods=['GET', 'POST'])
def login():
    """Render login page."""
    status = ''
    data = {}

    if 'user_id' in session:
        del session['user_id']
        if request.referrer:
            return redirect(request.referrer)
        return redirect(url_for('routes.login'))

    if request.method == 'POST':
        data = request.form.to_dict()
        status = Users().login_user(
            data.get('email'), data.get('password'))
        if not status:
            return redirect(url_for('routes.home'))

    return render_template('login.html', data=data, status=status)


@routes.route('/account/', methods=['GET', 'POST'])
@req_user_login()
def account():
    """Render the account page."""
    return render_template('account.html')


@routes.route('/projects/')
@req_user_login()
def projects():
    """Page with the list of all projects."""
    proj = Projects()
    projects = proj.all_by_field('owner', g.user.id)

    proj.join('contributors', 'id=project_id', ['user_id', 'permissions'])
    contributions = proj.all_by_field('user_id', g.user.id)
    proj.clear_joins()

    return render_template('projects.html', projects=projects,
                           contributions=contributions)


@routes.route('/projects/<project_id>')
@req_user_login()
def project(project_id):
    """Page with the list of all projects."""
    project = Projects().get(id=project_id)
    revisions = Revisions().all_by_field('project_id', project_id)
    issues = Issues().all_by_field('project_id', project_id)
    return render_template('project.html', revisions=revisions, project=project,
                           issues=issues)


@routes.route('/projects/<project_id>/rev/<revision_id>')
@req_user_login()
def revision(project_id, revision_id):
    """Page with the list of all projects."""
    project = Projects().get(id=project_id)
    revision = Revisions().get(project_id=project_id, revision_id=revision_id)
    diff = revision.get('diff')
    lexer = get_lexer_by_name("diff", stripall=True)
    formatter = HtmlFormatter(style=get_style_by_name('colorful'))
    formatted_diff = highlight(diff, lexer, formatter)
    user = Users().get(id=revision.get('contributor_id'))
    return render_template('revision.html', revision=revision, project=project,
                           user=user, diff=formatted_diff,
                           diff_styles=HtmlFormatter().get_style_defs(
                               '.highlight'))


@routes.route('/projects/<project_id>/issue/<issue_id>',
              methods=['GET', 'POST'])
@req_user_login()
def issue(project_id, issue_id):
    """Return the list of issues."""
    project = Projects().get(id=project_id)
    issue = Issues().get(project_id=project_id, issue_id=issue_id)

    if request.method == 'POST':
        new_comment_id = db.execute(
            'SELECT new_issue_comment_id({}, {}) AS id;'.format(
                project_id, issue_id)).fetchone()
        form = {
            'project_id': project_id,
            'issue_id': issue_id,
            'comment_id': new_comment_id.get('id'),
            'title': request.form.get('title'),
            'comment': request.form.get('comment'),
            'commenter': g.user.id
        }
        Issue_comments().add(form)

    if request.args.get('resolve'):
        Issues().update({'status': 'resolved'},
                        where='project_id={} AND issue_id={}'.format(
                            project_id, issue_id))
        return redirect(
            url_for('routes.issue', issue_id=issue_id, project_id=project_id))
    if request.args.get('close'):
        Issues().update({'status': 'closed'},
                        where='project_id={} AND issue_id={}'.format(
                            project_id, issue_id))
        return redirect(
            url_for('routes.issue', issue_id=issue_id, project_id=project_id))

    comments = Issue_comments().all(
        'issue_id=%(issue_id)s AND project_id=%(project_id)s',
        {'issue_id': issue_id, 'project_id': project_id}
    )
    for comment in comments:
        comment['user'] = Users().get(id=comment.get('commenter'))
    return render_template('issues.html', project=project, issue=issue,
                           comments=comments)


@routes.route('/projects/<project_id>/issue/new', methods=['GET', 'POST'])
@req_user_login()
def create_issue(project_id):
    """Page with the list of all projects."""
    project = Projects().get(id=project_id)

    if request.method == 'POST':
        new_issue_id = db.execute(
            'SELECT new_issue_id({}) AS id;'.format(project_id)).fetchone()
        form = {
            'project_id': project_id,
            'issue_id': new_issue_id.get('id'),
            'name': request.form.get('name'),
            'description': request.form.get('description')
        }
        Issues().add(form)
        return redirect(url_for('routes.project', project_id=project_id))

    return render_template('issue-new.html', project=project)


@routes.route('/projects/new/', methods=['GET', 'POST'])
@req_user_login()
def create_project():
    """Page to create a new project."""
    status = ''
    if request.method == 'POST':
        name = request.form.get('name')
        desc = request.form.get('description', '')

        if name:
            try:
                Projects().create(name, desc)
                return redirect(url_for('routes.projects'))
            except Exception as e:
                status = 'Error: {}'.format(str(e))
        else:
            status = 'Please specify the name of the project.'

    return render_template('projects-new.html', status=status)


@routes.route('/contributions/')
@req_user_login()
def contributions():
    """Page to list user's contributions."""
    contributions = Revisions().all_by_field('contributor_id', g.user.id)
    for cont in contributions:
        cont['project'] = Projects().get(id=cont.get('project_id'))
    return render_template('contributions.html', contributions=contributions)
