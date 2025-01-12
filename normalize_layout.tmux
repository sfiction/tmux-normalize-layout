#!/bin/bash

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

NORM="$ROOT/normalize_layout.sh"

main() {
    tmux bind-key M-7 run-shell "$NORM equal"
    tmux bind-key M-8 run-shell "$NORM grid"
    tmux bind-key M-9 run-shell "$NORM fit"
    tmux bind-key M-0 run-shell "$NORM area"
    tmux bind-key -n M-c run-shell "$NORM"
    # tmux set-option -gq @normalize-layout-strategy fit
}
main
