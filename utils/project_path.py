from os import path


class ProjectPath:
    utils_path = path.abspath(path.dirname(__file__))
    root_path = path.dirname(utils_path)
    datasets_path = path.join(root_path, 'datasets')
    dataset_backup_path = path.join(root_path, 'dataset_backup')
    config_path = path.join(root_path, 'config')
    yamls_path = path.join(root_path, 'yamls')


if __name__ == '__main__':
    print(ProjectPath.root_path)
