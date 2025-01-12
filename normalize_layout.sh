#!/bin/bash

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

get() {
    tmux display-message -p -F "#{$1}"
}

main() {
    old_layout=$(get window_layout)
    adjust=fit
    border=$(get pane-border-status)
    layout=$(python3 "$ROOT/normalize_layout.py" --adjust "$adjust" --border "$border" "$old_layout")
    if [[ -n $layout ]]; then
        tmux select-layout "$layout"
        tmux display-message -d 200 'layout normalized'
    else
        tmux display-message "failed to change layout $old_layout with $adjust $border to $layout"
        exit 1
    fi
}

main
