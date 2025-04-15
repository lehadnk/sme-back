create type user_role as enum('admin', 'researcher', 'user');
create type regression_model as enum('gradient_boosting', 'random_forest', 'xgboost');

create table users(
    id bigserial primary key,
    role user_role not null,
    username varchar not null unique,
    password varchar not null
);

create table models(
    id bigserial primary key,
    author_id int not null references users("id") on delete restrict,
    train_data_from timestamp not null,
    train_data_to timestamp not null,
    ticker varchar not null,
    rmse float not null,
    min float not null,
    max float not null,
    regression_model regression_model not null,
    model_filename varchar not null
);

create table experiments(
    id bigserial primary key,
    author_id int not null references users("id") on delete restrict,
    train_data_from timestamp not null,
    train_data_to timestamp not null,
    test_data_from timestamp not null,
    test_data_to timestamp not null,
    ticker varchar not null,
    rmse float not null,
    min float not null,
    max float not null,
    regression_model regression_model not null,
    model_filename varchar not null
);

create table predictions(
    id bigserial primary key,
    model_id int references models("id") on delete restrict,
    date timestamp not null,
    price float not null
);