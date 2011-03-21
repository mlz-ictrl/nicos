/********************************************************************************
** Form generated from reading UI file 'servercfgu32707.ui'
**
** Created
**      by: Qt User Interface Compiler version 4.6.3
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef SERVERCFGU32707_H
#define SERVERCFGU32707_H

#include <QtCore/QVariant>
#include <QtGui/QAction>
#include <QtGui/QApplication>
#include <QtGui/QButtonGroup>
#include <QtGui/QDialog>
#include <QtGui/QDialogButtonBox>
#include <QtGui/QHBoxLayout>
#include <QtGui/QHeaderView>
#include <QtGui/QLabel>
#include <QtGui/QLineEdit>
#include <QtGui/QWidget>

QT_BEGIN_NAMESPACE

class Ui_ServerConfigDlg
{
public:
    QDialogButtonBox *buttonBox;
    QWidget *widget;
    QHBoxLayout *horizontalLayout;
    QLabel *label;
    QLineEdit *editMeasTime;

    void setupUi(QDialog *ServerConfigDlg)
    {
        if (ServerConfigDlg->objectName().isEmpty())
            ServerConfigDlg->setObjectName(QString::fromUtf8("ServerConfigDlg"));
        ServerConfigDlg->resize(287, 140);
        buttonBox = new QDialogButtonBox(ServerConfigDlg);
        buttonBox->setObjectName(QString::fromUtf8("buttonBox"));
        buttonBox->setGeometry(QRect(80, 100, 201, 32));
        buttonBox->setOrientation(Qt::Horizontal);
        buttonBox->setStandardButtons(QDialogButtonBox::Cancel|QDialogButtonBox::Ok);
        widget = new QWidget(ServerConfigDlg);
        widget->setObjectName(QString::fromUtf8("widget"));
        widget->setGeometry(QRect(10, 10, 271, 26));
        horizontalLayout = new QHBoxLayout(widget);
        horizontalLayout->setObjectName(QString::fromUtf8("horizontalLayout"));
        horizontalLayout->setContentsMargins(0, 0, 0, 0);
        label = new QLabel(widget);
        label->setObjectName(QString::fromUtf8("label"));

        horizontalLayout->addWidget(label);

        editMeasTime = new QLineEdit(widget);
        editMeasTime->setObjectName(QString::fromUtf8("editMeasTime"));

        horizontalLayout->addWidget(editMeasTime);


        retranslateUi(ServerConfigDlg);
        QObject::connect(buttonBox, SIGNAL(accepted()), ServerConfigDlg, SLOT(accept()));
        QObject::connect(buttonBox, SIGNAL(rejected()), ServerConfigDlg, SLOT(reject()));

        QMetaObject::connectSlotsByName(ServerConfigDlg);
    } // setupUi

    void retranslateUi(QDialog *ServerConfigDlg)
    {
        ServerConfigDlg->setWindowTitle(QApplication::translate("ServerConfigDlg", "Configure", 0, QApplication::UnicodeUTF8));
        label->setText(QApplication::translate("ServerConfigDlg", "Measurement Time (in s):", 0, QApplication::UnicodeUTF8));
    } // retranslateUi

};

namespace Ui {
    class ServerConfigDlg: public Ui_ServerConfigDlg {};
} // namespace Ui

QT_END_NAMESPACE

#endif // SERVERCFGU32707_H
