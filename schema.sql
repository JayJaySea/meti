create table projects (
    id uuid primary key,
    name text unique not null,
    is_template boolean not null,
    last_accessed integer,
    view_x integer,
    view_y integer,
    zoomed_out boolean not null
);

create table checklist_templates (
    id uuid primary key,
    title text not null
);

create table template_checks (
    id uuid primary key,
    template_id uuid references checklist_templates(id),
    content text not null,
    position integer not null
);

create table checklists (
    id uuid primary key,
    template_id uuid references checklist_templates(id),
    project_id uuid references projects(id) not null,
    parent_id uuid references checklists(id),
    title text not null,
    position_x integer not null,
    position_y integer not null
);

create table checks (
    id uuid primary key,
    checklist_id uuid references checklists(id),
    content text not null,
    state integer not null,
    position integer not null
);

insert into projects values ('79c9ef23-050c-4d2c-8789-aab3b2009390', "test", false, 1745247663, null, null, false);
insert into checklists values ('3600dc0e-38c3-4b88-8846-8739b5de95f3', null, "79c9ef23-050c-4d2c-8789-aab3b2009390", null, "test", 100, 100);
insert into checks values ('bc247ed8-8d55-419d-87f5-51de7a06b480', '3600dc0e-38c3-4b88-8846-8739b5de95f3', "Yay it works", 1, 0);
insert into checks values ('890632ad-55ab-4add-a2c2-40aaa017a114', '3600dc0e-38c3-4b88-8846-8739b5de95f3', "Nice, should be second", 0, 1);

insert into checklists values ('b0e60b13-673f-473e-9029-d7fba19fb644', null, "79c9ef23-050c-4d2c-8789-aab3b2009390", '3600dc0e-38c3-4b88-8846-8739b5de95f3', "Another checklist", 500, 100);
insert into checks values ('482f1355-07dd-4e10-8ece-ed128eacd0fe', 'b0e60b13-673f-473e-9029-d7fba19fb644', "Second checklist first item", 1, 0);
insert into checks values ('6e313a15-60fe-40c8-8557-4580e16be4ae', 'b0e60b13-673f-473e-9029-d7fba19fb644', "Second checklist second item", 1, 1);
insert into checks values ('27424da7-d99e-4a5d-8b5b-ae2c8aebedfe', 'b0e60b13-673f-473e-9029-d7fba19fb644', "Second checklist third item", 0, 2);
insert into checks values ('65f96972-5d57-459f-af0a-8e92a3f12b5c', 'b0e60b13-673f-473e-9029-d7fba19fb644', "Second checklist fourth item", 0, 3);
