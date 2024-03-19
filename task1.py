#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Standard
import os
import sys
import argparse
from random import randint
import json
import jsonschema


def add_train(trains, num, destination, start_time):
    """
    Добавляет информацию о поезде в список trains.

    Args:
    - trains (list): Список поездов.
    - num (int): Номер поезда.
    - destination (str): Пункт назначения.
    - start_time (str): Время отправки

    Returns:
    - trains (list): Список поездов.
    """
    trains.append({
        'num': num,
        'destination': destination,
        'start_time': start_time
    })
    if len(trains) > 1:
        trains.sort(key=lambda item: item['start_time'])

    return trains


def save_trains(file_name, trains):
    """
    Сохраняет список поездов в файл в формате JSON.

    Args:
    - file_name (str): Имя файла.
    - trains (list): Список поездов.

    """
    with open(file_name, "w", encoding="utf-8") as fout:
        json.dump(trains, fout, ensure_ascii=False, indent=4)


def load_trains(file_name):
    """
    Загружает список поездов из файла в формате JSON.

    Args:
    - file_name (str): Имя файла.

    Returns:
    - trains (list): Список поездов.

    """
    with open(file_name, "r", encoding="utf-8") as fin:
        loaded_data = json.load(fin)

    with open('scheme.json', 'r', encoding='utf-8') as scheme_file:
        scheme = json.load(scheme_file)

    try:
        jsonschema.validate(loaded_data, scheme)
        return loaded_data
    except jsonschema.exceptions.ValidationError as e:
        print('Ошибка валидации данных:', e)
        return None


def display_trains(trains):
    """
    Выводит список поездов на экран.

    Args:
    - trains (list): Список поездов.

    """
    line = f'+-{"-" * 15}-+-{"-" * 30}-+-{"-" * 25}-+'
    print(line)
    header = f"| {'№ поезда':^15} | {'Пункт назначения':^30} | {'Время отъезда':^25} |"
    print(header)
    print(line)
    for train in trains:
        num = train.get('num', randint(1000, 10000))
        destination = train.get('destination', 'None')
        start_time = train.get('start_time', 'None')
        recording = f"| {num:^15} | {destination:^30} | {start_time:^25} |"
        print(recording)
    print(line)


def select_trains(trains, destination):
    """
    Выводит информацию о поездах, направляющихся в указанный пункт.

    Args:
    - trains (list): Список поездов.
    - destination (list): Пункт назначения.

    Returns:
    - trains (list): Список поездов.

    """

    return [train for train in trains if train['destination'].strip() == destination]


def main(command_line=None):
    # Creating file parser
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        '--data',
        action="store",
        required=False,
        help="The data file name"
    )

    # Main parser of command line
    parser = argparse.ArgumentParser("trains")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )

    # Subparsers
    subparsers = parser.add_subparsers(dest="command")

    # Subparser for add command
    add = subparsers.add_parser(
        "add",
        parents=[file_parser],
        help="Add a new train"
    )
    add.add_argument(
        "-n",
        "--number",
        action="store",
        required=True,
        type=int,
        help="The number of a train"
    )
    add.add_argument(
        "-d",
        "--destination",
        action="store",
        required=True,
        help="Destination point"
    )
    add.add_argument(
        "-st",
        "--start_time",
        action="store",
        required=True,
        help="Depart time"
    )

    # Subparser for display command
    display = subparsers.add_parser(
        "display",
        parents=[file_parser],
        help="Display all trains"
    )

    # Subparser for select command
    select = subparsers.add_parser(
        'select',
        parents=[file_parser],
        help='Select trains by destination'
    )

    select.add_argument(
        "-D",
        "--dest",
        action="store",
        required=True,
        help="The required destination"
    )

    args = parser.parse_args(command_line)

    # Получить имя файла
    data_file = args.data
    if not data_file:
        data_file = os.environ.get('TRAINS_DATA')
    if not data_file:
        print('The data file name is absent', file=sys.stderr)
        sys.exit(1)

    is_dirty = False
    if os.path.exists(data_file):
        trains = load_trains(data_file)
    else:
        trains = []

    match args.command:
        case 'add':
            trains = add_train(
                trains,
                args.number,
                args.destination,
                args.start_time
            )
            is_dirty = True
        case 'display':
            display_trains(trains)
        case 'select':
            selected = select_trains(trains, args.dest)
            display_trains(selected)

    # Save changes in file if data is changed
    if is_dirty:
        save_trains(data_file, trains)


if __name__ == '__main__':
    os.environ.setdefault('TRAINS_DATA', 'trains.json')
    main()
