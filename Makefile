MANAGER = poetry run

pdf_to_image:
	$(MANAGER) python to_latex_converter/tools/pdf_to_image.py --config configs/data_preprocess.yaml

