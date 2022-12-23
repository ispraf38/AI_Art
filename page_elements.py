
PHILLIPS_PAGE_ELEMENTS = {
    'page_widget': (
        'div',
        {
            'class': 'pager'
        }
    ),
    'page_list': (
        'span',
        {
            'class': 'num'
        }
    ),
    'page_button': (
        'a',
        {}
    ),
}

PHILLIPS_LOT_ELEMENTS = {
    'lot_box_container': (
        'ul',
        {
            'class': 'standard-grid row search-results',
            'id': 'main-list-backbone'
        }
    ),
    'lot_box': (
        'li',
        {
            'class': 'col-xs-6 col-sm-3 search-result-item'
        }
    ),
    'lot_link': (
        'a',
        {
            'class': 'image-link'
        }
    )
}

PHILLIPS_RESULTS_ELEMENTS = {
    'results': (
        'h1',
        {
            'class': 'item-count-display'
        }
    ),
}

CHRISTIES_PAGE_ELEMENTS = {
    'page_list': (
        'ul',
        {
            'class': 'chr-page-pagination__list'
        }
    ),
    'page_button': (
        'li',
        {}
    ),
    'page_text': (
        'span',
        {
            'class': 'chr-button__text'
        }
    ),
}

CHRISTIES_LOT_ELEMENTS = {
    'lot_box_container': (
        'div',
        {
            'class': 'chr-search-lots-view__column-transition col-12 col-lm-8 col-lg-9 col-xl-9'
        }
    ),
    'lot_box': (
        'div',
        {
            'class': 'chr-search-lots-view__column-transition chr-search-lots-view__tile-section col-sm-6 col-md-4 '
                     'chr-search-results tile-gutter col-lm-6 col-lg-4 col-xl-4'
        }
    ),
    'lot_link': (
        'a',
        {
            'class': 'chr-lot-tile__link'
        }
    )
}

CHRISTIES_RESULTS_ELEMENTS = {
    'results_carousel': (
        'div',
        {
            'class': 'chr-scrolling-carousel__content'
        }
    ),
    'results_button': (
        'button',
        {
            'title': 'Sold Lots'
        }
    ),
    'results_num': (
        'span',
        {}
    )
}