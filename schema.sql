create table projects (
    id uuid primary key,
    name text unique,
    is_template boolean,
    last_accessed integer
);

create table checklist_templates (
    id uuid primary key,
    title text
);

create table checklists (
    id uuid primary key,
    template_id uuid references checklist_templates(id) not null,
    project_id uuid references projects(id) not null,
    parent uuid references checklists(id),
    state text,
    position_x integer,
    position_y integer
);

create table checks (
    id uuid primary key,
    template_id uuid references checklist_templates(id),
    content text,
    position integer
);

insert into projects values ('79c9ef23-050c-4d2c-8789-aab3b2009390', "test", false, 1745247663);
insert into checklist_templates values ('285ed465-0ec4-4e1f-9b4c-24271577d81f', "Test");
insert into checklists values ('3600dc0e-38c3-4b88-8846-8739b5de95f3', '285ed465-0ec4-4e1f-9b4c-24271577d81f', "79c9ef23-050c-4d2c-8789-aab3b2009390", null, "01", 100, 100);
insert into checks values ('bc247ed8-8d55-419d-87f5-51de7a06b480', '285ed465-0ec4-4e1f-9b4c-24271577d81f', "Yay it works", 0);
insert into checks values ('890632ad-55ab-4add-a2c2-40aaa017a114', '285ed465-0ec4-4e1f-9b4c-24271577d81f', "Nice, should be second", 1);

insert into checklist_templates values ('6a5b1aae-1d0b-4c78-96e6-0935c8606ce0', "Another checklist");
insert into checklists values ('b0e60b13-673f-473e-9029-d7fba19fb644', '6a5b1aae-1d0b-4c78-96e6-0935c8606ce0', "79c9ef23-050c-4d2c-8789-aab3b2009390", '3600dc0e-38c3-4b88-8846-8739b5de95f3', "1100", 500, 100);
insert into checks values ('482f1355-07dd-4e10-8ece-ed128eacd0fe', '6a5b1aae-1d0b-4c78-96e6-0935c8606ce0', "Second checklist first item", 0);
insert into checks values ('6e313a15-60fe-40c8-8557-4580e16be4ae', '6a5b1aae-1d0b-4c78-96e6-0935c8606ce0', "Second checklist second item", 1);
insert into checks values ('27424da7-d99e-4a5d-8b5b-ae2c8aebedfe', '6a5b1aae-1d0b-4c78-96e6-0935c8606ce0', "Second checklist third item", 2);
insert into checks values ('65f96972-5d57-459f-af0a-8e92a3f12b5c', '6a5b1aae-1d0b-4c78-96e6-0935c8606ce0', "Second checklist fourth item", 3);
