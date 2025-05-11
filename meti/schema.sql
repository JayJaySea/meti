create table projects (
    id uuid primary key,
    title text unique not null,
    is_template boolean not null,
    last_accessed integer,
    view_x integer,
    view_y integer,
    zoomed_out boolean not null
);

create table checklist_templates (
    id uuid primary key,
    title text not null,
    color text,
    note_id text
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
    position_y integer not null,
    color text,
    note_id text
);

create table checks (
    id uuid primary key,
    checklist_id uuid references checklists(id),
    content text not null,
    state integer not null,
    position integer not null
);

insert into projects values ('79c9ef23-050c-4d2c-8789-aab3b2009390', "test", false, 1745247663, null, null, false);
