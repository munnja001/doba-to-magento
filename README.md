doba-to-magento
===============
Utilities that assist in process of managing catalogs between Doba standard and Magento Community

    Uploads product data, inventory data, and images. Coming soon... This does not yet do an inventory only upload

    use -c to specify a category for the imports

Must use python 2

1. Go to doba and download your product export.
2. Update config.py with your config settings
2. Run the doba to magento script with ./doba-to-magento.py pathToExportFile
3. Update Import Behavior to be "Replace Existing Complex Data"
3. Upload the magento-export-magento.csv to your magento instance
