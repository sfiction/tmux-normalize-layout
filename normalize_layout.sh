#!/bin/bash

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SUCCESS_DELAY=500

get() {
    tmux display-message -p -F "#{$1}"
}

main() {
    old_layout=$(get window_layout)
    border=$(get pane-border-status)

    strategy=${1:-$(get @normalize_layout-strategy)}
    ${strategy:=fit}
    layout=$(python3 "$ROOT/normalize_layout.py" --strategy "$strategy" --border "$border" "$old_layout")
    if [[ -n $layout ]]; then
        tmux select-layout "$layout"
        tmux display-message -d $SUCCESS_DELAY 'layout normalized'
    else
        tmux display-message "failed to change layout $old_layout with $strategy $border to $layout"
        exit 1
    fi
}

main
