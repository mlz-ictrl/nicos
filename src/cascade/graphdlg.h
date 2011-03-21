/********************************************************************************
** Form generated from reading UI file 'graphdlgKk3011.ui'
**
** Created
**      by: Qt User Interface Compiler version 4.6.3
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef GRAPHDLGKK3011_H
#define GRAPHDLGKK3011_H

#include <QtCore/QLocale>
#include <QtCore/QVariant>
#include <QtGui/QAction>
#include <QtGui/QApplication>
#include <QtGui/QButtonGroup>
#include <QtGui/QDialog>
#include <QtGui/QDialogButtonBox>
#include <QtGui/QDoubleSpinBox>
#include <QtGui/QGridLayout>
#include <QtGui/QGroupBox>
#include <QtGui/QHBoxLayout>
#include <QtGui/QHeaderView>
#include <QtGui/QLabel>
#include <QtGui/QSpinBox>
#include <QtGui/QVBoxLayout>
#include <qwt/qwt_plot.h>

QT_BEGIN_NAMESPACE

class Ui_GraphDlg
{
public:
    QVBoxLayout *verticalLayout;
    QwtPlot *qwtPlot;
    QGroupBox *groupBox;
    QHBoxLayout *horizontalLayout;
    QGridLayout *gridLayout;
    QLabel *label;
    QSpinBox *spinBoxROIx1;
    QLabel *label_2;
    QSpinBox *spinBoxROIx2;
    QLabel *label_3;
    QSpinBox *spinBoxROIy1;
    QLabel *label_4;
    QSpinBox *spinBoxROIy2;
    QLabel *label_5;
    QSpinBox *spinBoxFolie;
    QLabel *label_6;
    QDoubleSpinBox *spinBoxPhase;
    QLabel *labelFit;
    QDialogButtonBox *buttonBox;

    void setupUi(QDialog *GraphDlg)
    {
        if (GraphDlg->objectName().isEmpty())
            GraphDlg->setObjectName(QString::fromUtf8("GraphDlg"));
        GraphDlg->resize(612, 541);
        verticalLayout = new QVBoxLayout(GraphDlg);
        verticalLayout->setObjectName(QString::fromUtf8("verticalLayout"));
        qwtPlot = new QwtPlot(GraphDlg);
        qwtPlot->setObjectName(QString::fromUtf8("qwtPlot"));

        verticalLayout->addWidget(qwtPlot);

        groupBox = new QGroupBox(GraphDlg);
        groupBox->setObjectName(QString::fromUtf8("groupBox"));
        QSizePolicy sizePolicy(QSizePolicy::Expanding, QSizePolicy::Preferred);
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        sizePolicy.setHeightForWidth(groupBox->sizePolicy().hasHeightForWidth());
        groupBox->setSizePolicy(sizePolicy);
        horizontalLayout = new QHBoxLayout(groupBox);
        horizontalLayout->setObjectName(QString::fromUtf8("horizontalLayout"));
        gridLayout = new QGridLayout();
        gridLayout->setObjectName(QString::fromUtf8("gridLayout"));
        label = new QLabel(groupBox);
        label->setObjectName(QString::fromUtf8("label"));

        gridLayout->addWidget(label, 0, 0, 1, 1);

        spinBoxROIx1 = new QSpinBox(groupBox);
        spinBoxROIx1->setObjectName(QString::fromUtf8("spinBoxROIx1"));

        gridLayout->addWidget(spinBoxROIx1, 0, 1, 1, 1);

        label_2 = new QLabel(groupBox);
        label_2->setObjectName(QString::fromUtf8("label_2"));

        gridLayout->addWidget(label_2, 0, 2, 1, 1);

        spinBoxROIx2 = new QSpinBox(groupBox);
        spinBoxROIx2->setObjectName(QString::fromUtf8("spinBoxROIx2"));

        gridLayout->addWidget(spinBoxROIx2, 0, 3, 1, 1);

        label_3 = new QLabel(groupBox);
        label_3->setObjectName(QString::fromUtf8("label_3"));

        gridLayout->addWidget(label_3, 1, 0, 1, 1);

        spinBoxROIy1 = new QSpinBox(groupBox);
        spinBoxROIy1->setObjectName(QString::fromUtf8("spinBoxROIy1"));

        gridLayout->addWidget(spinBoxROIy1, 1, 1, 1, 1);

        label_4 = new QLabel(groupBox);
        label_4->setObjectName(QString::fromUtf8("label_4"));

        gridLayout->addWidget(label_4, 1, 2, 1, 1);

        spinBoxROIy2 = new QSpinBox(groupBox);
        spinBoxROIy2->setObjectName(QString::fromUtf8("spinBoxROIy2"));

        gridLayout->addWidget(spinBoxROIy2, 1, 3, 1, 1);

        label_5 = new QLabel(groupBox);
        label_5->setObjectName(QString::fromUtf8("label_5"));

        gridLayout->addWidget(label_5, 2, 0, 1, 1);

        spinBoxFolie = new QSpinBox(groupBox);
        spinBoxFolie->setObjectName(QString::fromUtf8("spinBoxFolie"));

        gridLayout->addWidget(spinBoxFolie, 2, 1, 1, 1);

        label_6 = new QLabel(groupBox);
        label_6->setObjectName(QString::fromUtf8("label_6"));

        gridLayout->addWidget(label_6, 2, 2, 1, 1);

        spinBoxPhase = new QDoubleSpinBox(groupBox);
        spinBoxPhase->setObjectName(QString::fromUtf8("spinBoxPhase"));
        spinBoxPhase->setDecimals(4);
        spinBoxPhase->setMinimum(-10);
        spinBoxPhase->setMaximum(10);
        spinBoxPhase->setSingleStep(0.1);

        gridLayout->addWidget(spinBoxPhase, 2, 3, 1, 1);


        horizontalLayout->addLayout(gridLayout);

        labelFit = new QLabel(groupBox);
        labelFit->setObjectName(QString::fromUtf8("labelFit"));
        sizePolicy.setHeightForWidth(labelFit->sizePolicy().hasHeightForWidth());
        labelFit->setSizePolicy(sizePolicy);
        labelFit->setTextFormat(Qt::PlainText);
        labelFit->setAlignment(Qt::AlignLeading|Qt::AlignLeft|Qt::AlignTop);
        labelFit->setWordWrap(true);

        horizontalLayout->addWidget(labelFit);


        verticalLayout->addWidget(groupBox);

        buttonBox = new QDialogButtonBox(GraphDlg);
        buttonBox->setObjectName(QString::fromUtf8("buttonBox"));
        buttonBox->setEnabled(true);
        buttonBox->setLocale(QLocale(QLocale::English, QLocale::UnitedStates));
        buttonBox->setOrientation(Qt::Horizontal);
        buttonBox->setStandardButtons(QDialogButtonBox::Ok);

        verticalLayout->addWidget(buttonBox);


        retranslateUi(GraphDlg);
        QObject::connect(buttonBox, SIGNAL(accepted()), GraphDlg, SLOT(accept()));
        QObject::connect(buttonBox, SIGNAL(rejected()), GraphDlg, SLOT(reject()));

        QMetaObject::connectSlotsByName(GraphDlg);
    } // setupUi

    void retranslateUi(QDialog *GraphDlg)
    {
        GraphDlg->setWindowTitle(QApplication::translate("GraphDlg", "Graph", 0, QApplication::UnicodeUTF8));
        groupBox->setTitle(QString());
        label->setText(QApplication::translate("GraphDlg", "ROI x1:", 0, QApplication::UnicodeUTF8));
        label_2->setText(QApplication::translate("GraphDlg", "ROI x2:", 0, QApplication::UnicodeUTF8));
        label_3->setText(QApplication::translate("GraphDlg", "ROI y1:", 0, QApplication::UnicodeUTF8));
        label_4->setText(QApplication::translate("GraphDlg", "ROI y2:", 0, QApplication::UnicodeUTF8));
        label_5->setText(QApplication::translate("GraphDlg", "Foil:", 0, QApplication::UnicodeUTF8));
        label_6->setText(QApplication::translate("GraphDlg", "Phase:", 0, QApplication::UnicodeUTF8));
        labelFit->setText(QApplication::translate("GraphDlg", "Fit: ", 0, QApplication::UnicodeUTF8));
    } // retranslateUi

};

namespace Ui {
    class GraphDlg: public Ui_GraphDlg {};
} // namespace Ui

QT_END_NAMESPACE

#endif // GRAPHDLGKK3011_H
