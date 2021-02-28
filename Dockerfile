FROM ubuntu:18.04

RUN apt update -y
RUN apt install -y python3 
RUN apt install -y postgresql
RUN apt install -y postgresql-contrib 
RUN apt install -y sudo 
RUN apt install -y expect
RUN apt install -y libpq-dev python3-dev
RUN apt install -y python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install alembic==1.5.2
RUN pip3 install click==7.1.2
RUN pip3 install easydict==1.9
RUN pip3 install Flask==1.1.2
RUN pip3 install Flask-Migrate==2.6.0
RUN pip3 install flask-serialize==0.0.6
RUN pip3 install Flask-SQLAlchemy==2.4.4
RUN pip3 install itsdangerous==1.1.0
RUN pip3 install Jinja2==2.11.2
RUN pip3 install Mako==1.1.4
RUN pip3 install MarkupSafe==1.1.1
RUN pip3 install psycopg2==2.8.6
RUN pip3 install psycopg2-binary==2.8.6
RUN pip3 install python-dateutil==2.8.1
RUN pip3 install python-editor==1.0.4
RUN pip3 install six==1.15.0
RUN pip3 install SQLAlchemy==1.3.22
RUN pip3 install Werkzeug==1.0.1
RUN apt install -y vim
#RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/10/main/pg_hba.conf
RUN service postgresql restart
COPY . /hostelmanagement
WORKDIR /hostelmanagement

#RUN python3 get-pip.py.1

RUN pip3 install -r requirement.txt

#RUN install.sh


ENTRYPOINT service postgresql restart && bash -c "./install.sh" && bash -c "python3 app.py"

#CMD ["python3", "app_v2.py"]
