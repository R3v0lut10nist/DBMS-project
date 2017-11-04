set foreign_key_checks=0;
Drop table if exists Student;
Drop table if exists Admin;
Drop table if exists Alumni;
Drop table if exists Grp;
Drop table if exists Mentor;
set foreign_key_checks=1;
set foreign_key_checks=0;
drop table if exists Merchandise;
drop table if exists Ordr;
set foreign_key_checks=1;
set foreign_key_checks=0;
drop table if exists Projects;
drop table if exists Workers;
drop table if exists Collaborations;
set foreign_key_checks=1;
set foreign_key_checks=0;
drop table if exists Events;
drop table if exists Participation;
set foreign_key_checks=1;
set foreign_key_checks=0;
drop table if exists Notifications;
set foreign_key_checks=1;
delete from auth_user where id>1;
alter table auth_user auto_increment=1;
set foreign_key_checks=0;
drop table if exists Meetings;
drop table if exists MeetingAttendees;
drop table if exists TrsnID;
set foreign_key_checks=1;

Create table Grp (
	Name varchar(20) NOT NULL,
	Head int,
	Primary Key (Name)
);

insert into Grp(Name) values("CPG"), ("ML"), ("InfoSec"), ("Dev"), ("Finance");

Create table Mentor (
	ID int NOT NULL AUTO_INCREMENT PRIMARY KEY,
	User int,
	Name varchar(30) NOT NULL,
	Branch varchar(20) NOT NULL,
	year int NOT NULL,
	grp varchar(20),
	Contact varchar(11) NOT NULL,
	FOREIGN KEY(User) REFERENCES auth_user(id)
);

Alter table Mentor add Constraint fkg FOREIGN Key(grp) REFERENCES Grp(Name) on delete set NULL;
Alter table Grp add Constraint fkm FOREIGN Key(Head) REFERENCES Mentor(ID) on delete set NULL;

Create table Student (
	ID int NOT NULL AUTO_INCREMENT PRIMARY KEY,
	mID int,
	User int,
	Name varchar(30) NOT NULL,
	Branch varchar(20) NOT NULL,
	year int NOT NULL,
	grp varchar(20) NOT NULL,
	Contact varchar(11) NOT NULL,
	FOREIGN KEY(grp) REFERENCES Grp(Name),
	FOREIGN KEY(mID) REFERENCES Mentor(ID),
	FOREIGN KEY(User) REFERENCES auth_user(id)
);

Create table Admin (
	mID int,
	Name varchar(30) NOT NULL,
	Post varchar(20) Primary KEY,
	FOREIGN KEY(mID) REFERENCES Mentor(ID)
);

Create table Alumni (
	mID int Primary Key,
	Name varchar(30) NOT NULL,
	Passing_year int,
	FOREIGN KEY(mID) REFERENCES Mentor(ID)
);


Create table Notifications (
	ID int NOT NULL auto_increment primary key,
	aid int,
	note varchar(200),
	date_time datetime,
	status varchar(10) default 'unread',
	foreign key(aid) references auth_user(id)
);

insert into auth_user(password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) values('pbkdf2_sha256$30000$7xp2o4Ve0MLh$2BHnWSTR+mDRBiA0tKdWo3nuHka+4uvytyBvxF6qn6s=', 1, 'kika', 'Karthik', 'Kumar', 'kikapoo@gmail.com', 1, 1, '2017-11-04 16:20:00');
insert into Mentor(User, Name, Branch, year, grp, Contact) values(2, 'Karthik Kumar', 'CSE', 3, 'CPG', '9759259201');
insert into Admin values(1, "Karthik Kumar", "General Secretary");
Insert into Notifications(aid,note,date_time) values(2, 'Welcome', '2017-11-04 16:20:00');

insert into auth_user(password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) values('pbkdf2_sha256$30000$ZvWxKBxN1tbI$pXGbuS4yPaoVmSvKGGEF6n/hUZkmQsiqYzmjKFHtyZY=', 1, 'manika', 'Manik', 'Goyal', 'manikapanda@gmail.com', 1, 1, '2017-11-04 16:20:00');
insert into Mentor(User, Name, Branch, year, grp, Contact) values(3, 'Manik Goyal', 'CSE', 3, 'ML', '9448348730');
insert into Admin values(2, "Manik Goyal", "Group Head - ML");
update Grp set Head=2 where Name="ML";
Insert into Notifications(aid,note,date_time) values(3, 'Welcome', '2017-11-04 16:20:00');

insert into auth_user(password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) values('pbkdf2_sha256$30000$NQgFRhaFpfDB$E1sBkgsI0Flfg7z6onB6C5og2Q+vvt1W6co6/KfX5Gc=', 1, 'prarn26', 'Pranjal', 'Jain', 'prarn26@gmail.com', 1, 1, '2017-11-04 16:20:00');
insert into Mentor(User, Name, Branch, year, grp, Contact) values(4, 'Pranjal Jain', 'CSE', 3, 'CPG', '9314904103');
insert into Admin values(3, "Pranjal Jain", "Group Head - CPG");
update Grp set Head=3 where Name="CPG";
Insert into Notifications(aid,note,date_time) values(4, 'Welcome', '2017-11-04 16:20:00');

insert into auth_user(password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) values('pbkdf2_sha256$30000$pExGPZf2sAfb$cklFtSfcC6i2bg8j7eUmoqqJ4z1k83WGuRkcPkpY38Q=', 1, 'abhi', 'Abhinav', 'Singh', 'abhinav@gmail.com', 1, 1, '2017-11-04 16:20:00');
insert into Mentor(User, Name, Branch, year, grp, Contact) values(5, 'Abhinav Singh', 'CSE', 3, 'Dev', '9214998413');
insert into Admin values(4, "Abhinav Singh", "Group Head - Dev");
update Grp set Head=4 where Name="Dev";
Insert into Notifications(aid,note,date_time) values(5, 'Welcome', '2017-11-04 16:20:00');

insert into auth_user(password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) values('pbkdf2_sha256$30000$94t2pV4uOhey$WoszF9YsAa3UxnznOnrPQlyM9QVsj6jU9rngdNVzM4w=', 1, 'dp', 'Deewashwer', 'Rathee', 'dprathee@gmail.com', 1, 1, '2017-11-04 16:20:00');
insert into Mentor(User, Name, Branch, year, grp, Contact) values(6, 'Deewashwer Rathee', 'CSE', 3, 'InfoSec', '9091094001');
insert into Admin values(5, "Deevashwer Rathee", "Group Head - InfoSec");
update Grp set Head=5 where Name="InfoSec";
Insert into Notifications(aid,note,date_time) values(6, 'Welcome', '2017-11-04 16:20:00');

insert into auth_user(password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) values('pbkdf2_sha256$30000$XjlmyobToXiY$9KYRgEAIB+ArLo7nl4x1jqImr2qzlFzLnPpgmCwThjA=', 1, 'sultan', 'Gaurav', 'Sultaniya', 'sultan@gmail.com', 1, 1, '2017-11-04 16:20:00');
insert into Mentor(User, Name, Branch, year, grp, Contact) values(7, 'Gaurav Sultaniya', 'CSE', 3, 'Finance', '9448348730');
insert into Admin values(6, "Gaurav Sultaniya", "Group Head - Finance");
update Grp set Head=6 where Name="Finance";
Insert into Notifications(aid,note,date_time) values(7, 'Welcome', '2017-11-04 16:20:00');

Create table Merchandise (
	ID int NOT NULL AUTO_INCREMENT PRIMARY KEY,
	design longblob,
	Price int NOT NULL,
	Designer varchar(20) NOT NULL
);

Create table Projects (
	mentor int,
	Topic varchar(20),
	StartDate date,
	Status varchar(10) default NULL,
	Description varchar(30),
	Primary Key (mentor, Topic, StartDate),
	Foreign Key (mentor) References Mentor(ID)
);

Create table Workers (
	student int,
	mentor int,
	Topic varchar(20),
	StartDate date,
	Primary Key(student, mentor, Topic, StartDate),
	Foreign Key(student) References Student(ID),
	Foreign Key(mentor, Topic, StartDate) References Projects(mentor, Topic, StartDate)
);

create table Events (
	mentor int,
	name varchar(20),
	date_time datetime,
	type varchar(15),
	Venue_or_link varchar(100),
	primary key(mentor, name, date_time),
	foreign key(mentor) references Mentor(ID)
);

create table Participation (
	ID int,
	mentor int,
	event varchar(20),
	date_time datetime,
	status int default NULL,
	primary key (ID, mentor, event, date_time),
	foreign key(ID) references Student(ID),
	foreign key(mentor, event, date_time) references Events(mentor, name, date_time)
);


Create table Meetings (
	id int primary key auto_increment,
	topic varchar(20),
	venue varchar(30),
	date_time datetime
);

Create table MeetingAttendees (
	meeting_id int,
	admin_id int,
	primary key(meeting_id, admin_id),
	foreign key(meeting_id) references Meetings(id),
	foreign key(admin_id) references Admin(mID)
);

Create table TrsnID (
	id int primary key auto_increment
);
