db_changed := if shell("diff -q --new-file ./schema.sql ./data/schema.sql || true") == "" { "" } else { "if [ -f ./data/schema.sql ]; then rm ./data/meti.db; fi" }

run:
    mkdir -p ./data/icons
    cp -r ./fonts ./data/
    cp ./schema.sql ./data/

    {{db_changed}}

    sassc ./style/main.scss ./data/style.css
    python ./scripts/color_icons.py --input-dir icons --colors style/colors.scss --output-dir ./data/icons --recolor '#ffffff'
    python src/app.py

install:
    mkdir -p "$HOME"/.local/share/achiever/icons
    cp -r ./fonts/ "$HOME"/.local/share/achiever/
    cp ./schema.sql "$HOME"/.local/share/achiever/
    sassc ./style/main.scss "$HOME"/.local/share/achiever/style.css
    python scripts/color_icons.py --input-dir icons --colors style/colors.scss --output-dir "$HOME".local/share/achiever/icons --recolor '#ffffff'
    todo!
