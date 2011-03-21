/********************************************************************************
** Form generated from reading UI file 'calibrationdlgQ16876.ui'
**
** Created
**      by: Qt User Interface Compiler version 4.6.3
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef CALIBRATIONDLGQ16876_H
#define CALIBRATIONDLGQ16876_H

#include <QtCore/QVariant>
#include <QtGui/QAction>
#include <QtGui/QApplication>
#include <QtGui/QButtonGroup>
#include <QtGui/QDialog>
#include <QtGui/QDialogButtonBox>
#include <QtGui/QHeaderView>
#include <QtGui/QVBoxLayout>
#include <qwt/qwt_plot.h>

QT_BEGIN_NAMESPACE

class Ui_CalibrationDlg
{
public:
    QVBoxLayout *verticalLayout;
    QwtPlot *qwtPlot;
    QDialogButtonBox *buttonBox;

    void setupUi(QDialog *CalibrationDlg)
    {
        if (CalibrationDlg->objectName().isEmpty())
            CalibrationDlg->setObjectName(QString::fromUtf8("CalibrationDlg"));
        CalibrationDlg->resize(576, 424);
        verticalLayout = new QVBoxLayout(CalibrationDlg);
        verticalLayout->setObjectName(QString::fromUtf8("verticalLayout"));
        qwtPlot = new QwtPlot(CalibrationDlg);
        qwtPlot->setObjectName(QString::fromUtf8("qwtPlot"));

        verticalLayout->addWidget(qwtPlot);

        buttonBox = new QDialogButtonBox(CalibrationDlg);
        buttonBox->setObjectName(QString::fromUtf8("buttonBox"));
        buttonBox->setOrientation(Qt::Horizontal);
        buttonBox->setStandardButtons(QDialogButtonBox::Ok);

        verticalLayout->addWidget(buttonBox);


        retranslateUi(CalibrationDlg);
        QObject::connect(buttonBox, SIGNAL(accepted()), CalibrationDlg, SLOT(accept()));
        QObject::connect(buttonBox, SIGNAL(rejected()), CalibrationDlg, SLOT(reject()));

        QMetaObject::connectSlotsByName(CalibrationDlg);
    } // setupUi

    void retranslateUi(QDialog *CalibrationDlg)
    {
        CalibrationDlg->setWindowTitle(QApplication::translate("CalibrationDlg", "Calibration", 0, QApplication::UnicodeUTF8));
    } // retranslateUi

};

namespace Ui {
    class CalibrationDlg: public Ui_CalibrationDlg {};
} // namespace Ui

QT_END_NAMESPACE

#endif // CALIBRATIONDLGQ16876_H
