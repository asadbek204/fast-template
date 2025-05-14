#!/bin/bash

# colors
end_="\x1b[0m"
# regular colors
white="\x1b[37m"
red="\x1b[31m"
green="\x1b[32m"
blue="\x1b[34m"
cyan="\x1b[36m"
gray="\x1b[37m"
# bold colors
b_white="\x1b[1;37m";
b_red="\x1b[1;31m"
b_green="\x1b[1;32m"
# underlined colors
u_white="\x1b[4;37m"

########################################
# gloabal vars
script_name="${b_green}./manage.sh${end_}"

entry="__main__.py";
gitignore=".gitignore"
src='src'
routers='routers.py'

## app vars
views='views.py'
models='models.py'
schemas='schemas.py'
########################################

settings="from os import getenv
from dotenv import load_dotenv
from dataclasses import dataclass

assert load_dotenv(), '.env not found'

@dataclass(frozen=True)
class Settings:
    host: str
    port: int

settings = Settings(host=getenv('HOST'), port=int(getenv('PORT')))
"
env="DOMAIN=localhost
PORT=8000"

function show_args {
    echo -e "${b_white}usage:${end_}";
    echo -e "    $script_name ${b_white}<command>${end_} ${gray}[...options]${end_}";
    echo -e "${b_white}commands:${end_}
  ${blue}- init${end_}      -- initialize project
  ${blue}- run${end_}       -- if no sub commands runs project  ${b_green}|${end_}  ${gray}ex: $script_name ${b_white}run${end_} <sub command>${end_}
                 ${gray}sub commands:${end_}
                    ${cyan}- container${end_}                   ${gray}|  ex: run container${end_}
  ${blue}- create${end_}    -- entity creator                   ${b_green}|${end_}  ${gray}ex: $script_name ${b_white}create <sub command>${end_}
                 ${gray}sub commands:${end_}
                    ${cyan}- app${end_}                         ${gray}|  ex: create app <app_name>${end_}
                    ${cyan}- image${end_}                       ${gray}|  ex: create image${end_}
                    ${cyan}- container${end_}                   ${gray}|  ex: create container${end_}
  ${blue}- add${end_}       -- add package to poetry            ${b_green}|${end_}  ${gray}ex: $script_name ${b_white}add <package_name>${end_}
  ${blue}- migrate${end_}   -- create migration                 ${b_green}|${end_}  ${gray}ex: $script_name ${b_white}add <comment>${end_}
  ${blue}- help${end_}      -- to get help                      ${b_green}|${end_}  ${gray}ex: $script_name ${b_white}help${end_}";
    echo "";
    echo -e "${b_white}options:${end_}";
    echo -e "  ${blue}--reload${end_}    -- hot reload                       ${gray}|  ex: --reload${end_}";
    echo -e "  ${blue}--host${end_}      -- host name or url                 ${gray}|  ex: --host=0.0.0.0${end_}";
    echo -e "  ${blue}--port${end_}      -- port number                      ${gray}|  ex: --port=8000${end_}";
    echo -e "  ${blue}--override${end_}  -- overrides existings on create    ${gray}|  ex: --override${end_}";
}

function how_to_run {
    echo -e "${white}use command ${b_white}run${gray} for run project${end_}";
    echo -e "  $script_name ${b_white}run${end_} ${gray}[...options]${end_}";
    echo "";
    echo -e "${b_white}options:${end_}";
    echo -e "    ${blue}--reload${end_}    -- hot reload                       ${gray}|  ex: --reload${end_}";
    echo -e "    ${blue}--host${end_}      -- host name or url                 ${gray}|  ex: --host=0.0.0.0${end_}";
    echo -e "    ${blue}--port${end_}      -- port                             ${gray}|  ex: --port=8000${end_}";
}

function init_project {
    version=$(python3 -V 2>&1 | sed 's/.* \([0-9]\).\([0-9]\).*/\1\2/')
    if [ $version -ge 31 ]
    then
        if ! test -d project || $1 -e "--override";
        then
            mkdir project;
        fi
        if ! test -d pyproject.toml || $1 -e "--override";
        then
            poetry init;
            poetry lock;
            echo "" >> pyproject.toml;
            poetry install --no-root;
            poetry add fastapi[all]
            poetry add sqlalchemy
            poetry add alembic
            clear;
        fi
        cd project;
        if ! test -d settings.py || $1 -e "--override";
        then
            echo "$settings" > settings.py;
            echo "$env" > .env;
        fi
        if ! test -d $src || $1 -e "--override";
        then
            mkdir $src;
            touch $src/__init__.py;
        fi

        if ! test -f $routers || $1 -e "--override";
        then
            echo "from $src import *" > $routers;
            echo "from fastapi import APIRouter" >> $routers;
            echo "router = APIRouter()" >> $routers;
        fi

        if ! test -f $entry || $1 -e "--override";
        then
            echo 'import uvicorn' > $entry;
            echo 'from fastapi import FastAPI' >> $entry;
            echo 'from routers import router' >> $entry;
            echo 'from settings import settings' >> $entry;
            echo '' >> $entry;
            echo '' >> $entry;
            echo 'app = FastAPI()' >> $entry;
            echo 'app.include_router(router)' >> $entry;
            echo '' >> $entry;
            echo '' >> $entry;
            echo '@app.get("/")' >> $entry;
            echo 'async def home():' >> $entry;
            echo '    return "hello"' >> $entry;
            echo '' >> $entry;
            echo '' >> $entry;
            echo 'def main():' >> $entry;
            echo '    uvicorn.run(app=app, host=settings.host, port=settings.port)' >> $entry;
            echo '' >> $entry;
            echo '' >> $entry;
            echo 'if __name__ == "__main__":' >> $entry;
            echo "    main()" >> $entry;
        fi
        echo ".venv" > $gitignore;
        echo "poetry.lock" >> $gitignore;
        echo "__pycache__" >> $gitignore;
        echo ".env" >> $gitignore;
        echo ".vscode/" >> $gitignore;
        echo ".idea/" >> $gitignore;
        echo "media/" >> $gitignore;
        how_to_run;
    else
        echo "python >= 3.12 not found";
    fi
}

function create_app {
    cd project;
    echo "router.include_router(${1}_router)" >> $routers;
    cd $src;
    echo "from .${1}.views import router as ${1}_router" >> __init__.py;
    echo "from .${1}.models import *" >> __init__.py;
    mkdir $1;
    cd $1;
    touch __init__.py;
    echo "from fastapi import APIRouter" > $views;
    echo "" >> $views;
    echo "router = APIRouter(prefix='/$1', tags=['$1'])" >> $views;
    echo "" >> $views;
    echo "" >> $views;
    echo "@router.get('/')" >> $views;
    echo "async def $1():" >> $views;
    echo "    return '$1'" >> $views;
    echo "# write your models here" > $models;
    echo "from pydantic import BaseModel" > $schemas
    echo "# write your schemas here" >> $schemas;
}

function create {
    case $1 in
        'app')
            if [ $# -lt 2 ]
            then
                echo "no app name";
            else
                create_app $2;
            fi
        ;;
        *)
            echo "wrong sub command";
        ;;
    esac
}

function main {
    if [ $# -lt 1 ] 
    then
        echo -e "${b_red}ERR:${red} no command${end_}";
        show_args
    else
        case $1 in
            'migrate')
                if [ $# -lt 2 ]
                then
                    echo -e "${b_red}ERR:${red} no migration name${end_}";
                else
                    cd project;
                    alembic revision --autogenerate -m $2;
                fi
            ;;
            'shell')
                poetry shell;
            ;;
            'init')
                init_project ${@:2};
            ;;
            'log')
                docker compose logs -f $2;
            ;;
            'start')
                docker compose up -d;
            ;;
            'stop')
                docker compose down;
            ;;
            'restart')
                docker compose down && docker compose up -d;
            ;;
            'create')
                create ${@:2};
            ;;
            'help')
                how_to_run;
            ;;
            *)
                echo -e "${b_red}ERR:${end_} ${red}wrong command${end_}";
                show_args;
            ;;
        esac
    fi
}

main ${@:1};
