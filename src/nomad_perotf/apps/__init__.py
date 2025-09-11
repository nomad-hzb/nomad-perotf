from nomad.config.models.plugins import AppEntryPoint
from nomad.config.models.ui import (
    App,
    Column,
    Dashboard,
    FilterMenu,
    FilterMenus,
    FilterMenuSizeEnum,
    Filters,
    Format,
    Layout,
    ModeEnum,
    RowActionNorth,
    RowActions,
    RowDetails,
    Rows,
    RowSelection,
    WidgetTerms,
)

from nomad_perotf.apps.solar_cell_overview import solar_cell_overview

solar_cell_overview_entry_point = AppEntryPoint(
    name='SolarCellOverview',
    description="""
      This app allows you to search **solar cell data** within NOMAD. The filter
      menu on the left and the shown default columns are specifically designed
      for solar cell exploration. The dashboard directly shows useful
      interactive statistics about the data.
    """,
    app=solar_cell_overview,
)

schema_name = 'nomad_perotf.schema_packages.perotf_package.peroTF_VoilaNotebook'
perotf_voila_app = AppEntryPoint(
    name='voila',
    description='Find and launch your Voila Tools.',
    app=App(
        # Label of the App
        label='Voila',
        # Path used in the URL, must be unique
        path='voila',
        # Used to categorize apps in the explore menu
        category='use cases',
        # Brief description used in the app menu
        description='Find and launch your Voila Tools.',
        # Longer description that can also use markdown
        readme='Find and launch your Voila Tools.',
        # Controls the available search filters. If you want to filter by
        # quantities in a schema package, you need to load the schema package
        # explicitly here. Note that you can use a glob syntax to load the
        # entire package, or just a single schema from a package.
        filters=Filters(
            include=[
                f'*#{schema_name}',
            ]
        ),
        # Dictionary of search filters that are always enabled for queries made
        # within this app. This is especially important to narrow down the
        # results to the wanted subset. Any available search filter can be
        # targeted here. This example makes sure that only entries that use
        # MySchema are included.
        filters_locked={'section_defs.definition_qualified_name': schema_name},
        filter_menus=FilterMenus(
            options={
                'custom_quantities': FilterMenu(
                    label='Notebooks', size=FilterMenuSizeEnum.L
                ),
                'author': FilterMenu(label='Author', size=FilterMenuSizeEnum.M),
                'metadata': FilterMenu(label='Visibility / IDs'),
            }
        ),
        columns=[
            Column(quantity=f'data.name#{schema_name}', selected=True),
            Column(
                quantity='entry_type', label='Entry type', align='left', selected=True
            ),
            Column(
                quantity='entry_create_time',
                label='Entry time',
                align='left',
                selected=True,
                format=Format(mode=ModeEnum.DATE),
            ),
            Column(
                quantity='upload_name',
                label='Upload name',
                align='left',
                selected=True,
            ),
            Column(
                quantity='authors',
                label='Authors',
                align='left',
                selected=True,
            ),
            Column(quantity='entry_id'),
            Column(quantity='upload_id'),
            Column(quantity=f'data.notebook_file#{schema_name}'),
        ],
        rows=Rows(
            actions=RowActions(
                options={
                    'launch': RowActionNorth(
                        tool_name='voila',
                        filepath=f'data.notebook_file#{schema_name}',
                    )
                }
            ),
            details=RowDetails(),
            selection=RowSelection(),
        ),
        dashboard=Dashboard(
            widgets=[
                WidgetTerms(
                    title='Voila Notebook Tags',
                    quantity='results.eln.tags',
                    scale='linear',
                    layout={
                        'lg': Layout(h=4, minH=3, minW=3, w=6, x=0, y=0),
                        'md': Layout(h=5, minH=3, minW=3, w=7, x=0, y=0),
                        'sm': Layout(h=6, minH=3, minW=3, w=6, x=0, y=0),
                        'xl': Layout(h=6, minH=3, minW=3, w=6, x=0, y=0),
                        'xxl': Layout(h=6, minH=3, minW=3, w=6, x=0, y=0),
                    },
                ),
                WidgetTerms(
                    title='Authors',
                    quantity='authors.name',
                    scale='linear',
                    layout={
                        'lg': Layout(h=4, minH=3, minW=3, w=6, x=0, y=0),
                        'md': Layout(h=5, minH=3, minW=3, w=7, x=0, y=0),
                        'sm': Layout(h=6, minH=3, minW=3, w=6, x=0, y=0),
                        'xl': Layout(h=6, minH=3, minW=3, w=6, x=0, y=0),
                        'xxl': Layout(h=6, minH=3, minW=3, w=6, x=0, y=0),
                    },
                ),
            ]
        ),
    ),
)
