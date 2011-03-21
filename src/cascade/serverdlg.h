/********************************************************************************
** Form generated from reading UI file 'serverRs2642.ui'
**
** Created
**      by: Qt User Interface Compiler version 4.6.3
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef SERVERRS2642_H
#define SERVERRS2642_H

#include <QtCore/QVariant>
#include <QtGui/QAction>
#include <QtGui/QApplication>
#include <QtGui/QButtonGroup>
#include <QtGui/QDialog>
#include <QtGui/QDialogButtonBox>
#include <QtGui/QFormLayout>
#include <QtGui/QGridLayout>
#include <QtGui/QGroupBox>
#include <QtGui/QHeaderView>
#include <QtGui/QLabel>
#include <QtGui/QLineEdit>
#include <QtGui/QSpacerItem>

QT_BEGIN_NAMESPACE

class Ui_dialogServer
{
public:
    QGridLayout *gridLayout;
    QGroupBox *groupBox;
    QFormLayout *formLayout;
    QLabel *label;
    QLineEdit *editAddress;
    QLabel *label_2;
    QLineEdit *editPort;
    QDialogButtonBox *buttonBox;
    QSpacerItem *verticalSpacer;

    void setupUi(QDialog *dialogServer)
    {
        if (dialogServer->objectName().isEmpty())
            dialogServer->setObjectName(QString::fromUtf8("dialogServer"));
        dialogServer->resize(284, 153);
        gridLayout = new QGridLayout(dialogServer);
        gridLayout->setObjectName(QString::fromUtf8("gridLayout"));
        groupBox = new QGroupBox(dialogServer);
        groupBox->setObjectName(QString::fromUtf8("groupBox"));
        QSizePolicy sizePolicy(QSizePolicy::Preferred, QSizePolicy::Fixed);
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        sizePolicy.setHeightForWidth(groupBox->sizePolicy().hasHeightForWidth());
        groupBox->setSizePolicy(sizePolicy);
        formLayout = new QFormLayout(groupBox);
        formLayout->setObjectName(QString::fromUtf8("formLayout"));
        label = new QLabel(groupBox);
        label->setObjectName(QString::fromUtf8("label"));

        formLayout->setWidget(0, QFormLayout::LabelRole, label);

        editAddress = new QLineEdit(groupBox);
        editAddress->setObjectName(QString::fromUtf8("editAddress"));

        formLayout->setWidget(0, QFormLayout::FieldRole, editAddress);

        label_2 = new QLabel(groupBox);
        label_2->setObjectName(QString::fromUtf8("label_2"));

        formLayout->setWidget(1, QFormLayout::LabelRole, label_2);

        editPort = new QLineEdit(groupBox);
        editPort->setObjectName(QString::fromUtf8("editPort"));

        formLayout->setWidget(1, QFormLayout::FieldRole, editPort);


        gridLayout->addWidget(groupBox, 0, 0, 1, 1);

        buttonBox = new QDialogButtonBox(dialogServer);
        buttonBox->setObjectName(QString::fromUtf8("buttonBox"));
        buttonBox->setOrientation(Qt::Horizontal);
        buttonBox->setStandardButtons(QDialogButtonBox::Cancel|QDialogButtonBox::Ok);

        gridLayout->addWidget(buttonBox, 2, 0, 1, 1);

        verticalSpacer = new QSpacerItem(20, 40, QSizePolicy::Minimum, QSizePolicy::Expanding);

        gridLayout->addItem(verticalSpacer, 1, 0, 1, 1);


        retranslateUi(dialogServer);
        QObject::connect(buttonBox, SIGNAL(accepted()), dialogServer, SLOT(accept()));
        QObject::connect(buttonBox, SIGNAL(rejected()), dialogServer, SLOT(reject()));

        QMetaObject::connectSlotsByName(dialogServer);
    } // setupUi

    void retranslateUi(QDialog *dialogServer)
    {
        dialogServer->setWindowTitle(QApplication::translate("dialogServer", "Connect to Server", 0, QApplication::UnicodeUTF8));
        groupBox->setTitle(QApplication::translate("dialogServer", "Server", 0, QApplication::UnicodeUTF8));
        label->setText(QApplication::translate("dialogServer", "Address:", 0, QApplication::UnicodeUTF8));
        label_2->setText(QApplication::translate("dialogServer", "Port:", 0, QApplication::UnicodeUTF8));
    } // retranslateUi

};

namespace Ui {
    class dialogServer: public Ui_dialogServer {};
} // namespace Ui

QT_END_NAMESPACE

#endif // SERVERRS2642_H
