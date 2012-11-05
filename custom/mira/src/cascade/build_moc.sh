#!/bin/bash

echo -e "building mocs..."

moc main/cascade.cpp -o main/cascade.moc
moc main/cascadewidget.h -o main/cascadewidget.moc
moc plot/plotter.h -o plot/plotter.moc
moc dialogs/cascadedialogs.h -o dialogs/cascadedialogs.moc
moc client/client.h -o client/client.moc
