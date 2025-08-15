import papermill as pm
from config.config_loader import Config
import yaml


class ProviderNotebookExecutor:
    def __init__(self, config: Config, common_paths, project_name="load_compilation"):
        """
        Initialize with Config instance and common path dict.
        Provider notebooks will be built dynamically from the provider params file.
        """
        self.config = config
        self.common_paths = common_paths
        self.project_name = project_name
        self.provider_notebooks = {}  # Will be populated when loading provider params

    def build_provider_notebooks(self, provider_names):
        """
        Dynamically build the dictionary mapping provider names to notebook file paths
        based on the providers found in the provider_params.yaml file.
        """
        provider_notebooks = {}
        for provider in provider_names:
            try:
                notebook_path = self.config.get_resolved_path("notebooks.load_compilation.provider_nb", provider=provider)
                provider_notebooks[provider] = notebook_path
            except Exception as e:
                print(f"Warning: could not resolve notebook path for provider '{provider}': {e}")
        return provider_notebooks

    def get_provider_path_mappings(self):
        """
        Define which common paths each provider needs.
        This could eventually be moved to config as well.
        """
        return {
            'creara': ['path_alias_elec', 'path_load_elec_clean'],
            'linkener': ['path_load_elec_linkener'],
        }

    def parse_provider_params(self, provider_name, provider_dict):
        """
        Normalize provider parameters from YAML dict into flattened params for notebook execution.
        """
        output = {}

        execute = provider_dict.get('execute', False)
        output['execute'] = execute

        params = provider_dict.get('params', {})
        if 'start_date' in params and 'end_date' in params:
            output['start_date'] = params['start_date']
            output['end_date'] = params['end_date']
        else:
            output['start_date'] = None
            output['end_date'] = None

        for key, value in params.items():
            if key not in ['start_date', 'end_date']:
                output[key] = value

        credentials = provider_dict.get('credentials', {})
        for key, value in credentials.items():
            output[key] = value

        # Append common paths specific to provider using dynamic mapping
        provider_path_mappings = self.get_provider_path_mappings()
        required_paths = provider_path_mappings.get(provider_name, [])
        
        for path_key in required_paths:
            if path_key in self.common_paths:
                output[path_key] = self.common_paths[path_key]
            else:
                print(f"Warning: Required path '{path_key}' not found for provider '{provider_name}'")
        
        return output

    def execute_provider_notebooks(self, provider_parameters):
        """
        Execute notebooks whose providers have execute=True.
        """
        for provider_name, notebook_path in self.provider_notebooks.items():
            params = provider_parameters.get(provider_name, {})
            execute_flag = params.get('execute', False)

            if not execute_flag:
                print(f"Skipping provider '{provider_name}': execute flag is False.")
                continue

            try:
                output_notebook_path = self.config.get_path(
                    f"outputs.{self.project_name}.notebooks.provider_nb", provider=provider_name
                )
            except Exception as e:
                print(f"Error resolving output path for provider '{provider_name}': {e}")
                continue

            print(f"Executing notebook for provider '{provider_name}' with parameters: {params}")

            try:
                pm.execute_notebook(
                    input_path=notebook_path,
                    output_path=output_notebook_path,
                    parameters=params,
                    log_output=True
                )
                print(f"Completed execution of '{provider_name}' notebook; output saved at: {output_notebook_path}")
            except Exception as e:
                print(f"Error executing notebook for provider '{provider_name}': {e}")

    def execute_workflow(self, provider_params_path):
        """
        Complete workflow: load provider params, parse them, and execute notebooks.
        Provider list is dynamically extracted from the provider_params.yaml file.
        """
        # Load the YAML config for providers
        with open(provider_params_path, 'r') as file:
            all_provider_params = yaml.safe_load(file)
        
        # Extract provider names from the loaded params file
        provider_names = list(all_provider_params.keys())
        print(f"Found providers in config: {provider_names}")
        
        # Build provider notebooks mapping based on discovered providers
        self.provider_notebooks = self.build_provider_notebooks(provider_names)
        
        # Parse parameters for each provider
        provider_parameters = {}
        for provider_name, provider_cfg in all_provider_params.items():
            provider_parameters[provider_name] = self.parse_provider_params(provider_name, provider_cfg)
        
        # Execute notebooks for providers with execute=True
        self.execute_provider_notebooks(provider_parameters)
