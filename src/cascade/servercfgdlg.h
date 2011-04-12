/********************************************************************************
** Form generated from reading UI file 'servercfgr25647.ui'
**
** Created
**      by: Qt User Interface Compiler version 4.6.3
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef SERVERCFGR25647_H
#define SERVERCFGR25647_H

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
    QWidget *layoutWidget;
    QHBoxLayout *horizontalLayout;
    QLabel *label;
    QLineEdit *editMeasTime;
    QWidget *layoutWidget_2;
    QHBoxLayout *horizontalLayout_2;
    QLabel *label_2;
    QLineEdit *editxres;
    QWidget *layoutWidget_3;
    QHBoxLayout *horizontalLayout_3;
    QLabel *label_3;
    QLineEdit *edityres;
    QWidget *layoutWidget_4;
    QHBoxLayout *horizontalLayout_4;
    QLabel *label_4;
    QLineEdit *edittres;

    void setupUi(QDialog *ServerConfigDlg)
    {
        if (ServerConfigDlg->objectName().isEmpty())
            ServerConfigDlg->setObjectName(QString::fromUtf8("ServerConfigDlg"));
        ServerConfigDlg->resize(290, 208);
        buttonBox = new QDialogButtonBox(ServerConfigDlg);
        buttonBox->setObjectName(QString::fromUtf8("buttonBox"));
        buttonBox->setGeometry(QRect(80, 170, 201, 32));
        buttonBox->setOrientation(Qt::Horizontal);
        buttonBox->setStandardButtons(QDialogButtonBox::Cancel|QDialogButtonBox::Ok);
        layoutWidget = new QWidget(ServerConfigDlg);
        layoutWidget->setObjectName(QString::fromUtf8("layoutWidget"));
        layoutWidget->setGeometry(QRect(10, 10, 271, 26));
        horizontalLayout = new QHBoxLayout(layoutWidget);
        horizontalLayout->setObjectName(QString::fromUtf8("horizontalLayout"));
        horizontalLayout->setContentsMargins(0, 0, 0, 0);
        label = new QLabel(layoutWidget);
        label->setObjectName(QString::fromUtf8("label"));

        horizontalLayout->addWidget(label);

        editMeasTime = new QLineEdit(layoutWidget);
        editMeasTime->setObjectName(QString::fromUtf8("editMeasTime"));

        horizontalLayout->addWidget(editMeasTime);

        layoutWidget_2 = new QWidget(ServerConfigDlg);
        layoutWidget_2->setObjectName(QString::fromUtf8("layoutWidget_2"));
        layoutWidget_2->setGeometry(QRect(10, 40, 271, 26));
        horizontalLayout_2 = new QHBoxLayout(layoutWidget_2);
        horizontalLayout_2->setObjectName(QString::fromUtf8("horizontalLayout_2"));
        horizontalLayout_2->setContentsMargins(0, 0, 0, 0);
        label_2 = new QLabel(layoutWidget_2);
        label_2->setObjectName(QString::fromUtf8("label_2"));

        horizontalLayout_2->addWidget(label_2);

        editxres = new QLineEdit(layoutWidget_2);
        editxres->setObjectName(QString::fromUtf8("editxres"));

        horizontalLayout_2->addWidget(editxres);

        layoutWidget_3 = new QWidget(ServerConfigDlg);
        layoutWidget_3->setObjectName(QString::fromUtf8("layoutWidget_3"));
        layoutWidget_3->setGeometry(QRect(10, 70, 271, 26));
        horizontalLayout_3 = new QHBoxLayout(layoutWidget_3);
        horizontalLayout_3->setObjectName(QString::fromUtf8("horizontalLayout_3"));
        horizontalLayout_3->setContentsMargins(0, 0, 0, 0);
        label_3 = new QLabel(layoutWidget_3);
        label_3->setObjectName(QString::fromUtf8("label_3"));

        horizontalLayout_3->addWidget(label_3);

        edityres = new QLineEdit(layoutWidget_3);
        edityres->setObjectName(QString::fromUtf8("edityres"));

        horizontalLayout_3->addWidget(edityres);

        layoutWidget_4 = new QWidget(ServerConfigDlg);
        layoutWidget_4->setObjectName(QString::fromUtf8("layoutWidget_4"));
        layoutWidget_4->setGeometry(QRect(10, 100, 271, 26));
        horizontalLayout_4 = new QHBoxLayout(layoutWidget_4);
        horizontalLayout_4->setObjectName(QString::fromUtf8("horizontalLayout_4"));
        horizontalLayout_4->setContentsMargins(0, 0, 0, 0);
        label_4 = new QLabel(layoutWidget_4);
        label_4->setObjectName(QString::fromUtf8("label_4"));

        horizontalLayout_4->addWidget(label_4);

        edittres = new QLineEdit(layoutWidget_4);
        edittres->setObjectName(QString::fromUtf8("edittres"));

        horizontalLayout_4->addWidget(edittres);


        retranslateUi(ServerConfigDlg);
        QObject::connect(buttonBox, SIGNAL(accepted()), ServerConfigDlg, SLOT(accept()));
        QObject::connect(buttonBox, SIGNAL(rejected()), ServerConfigDlg, SLOT(reject()));

        QMetaObject::connectSlotsByName(ServerConfigDlg);
    } // setupUi

    void retranslateUi(QDialog *ServerConfigDlg)
    {
        ServerConfigDlg->setWindowTitle(QApplication::translate("ServerConfigDlg", "Configure", 0, QApplication::UnicodeUTF8));
        label->setText(QApplication::translate("ServerConfigDlg", "Measurement Time (in s):", 0, QApplication::UnicodeUTF8));
        label_2->setText(QApplication::translate("ServerConfigDlg", "x Resolution:", 0, QApplication::UnicodeUTF8));
        label_3->setText(QApplication::translate("ServerConfigDlg", "y Resolution:", 0, QApplication::UnicodeUTF8));
        label_4->setText(QApplication::translate("ServerConfigDlg", "Time Resolution:", 0, QApplication::UnicodeUTF8));
    } // retranslateUi

};

namespace Ui {
    class ServerConfigDlg: public Ui_ServerConfigDlg {};
} // namespace Ui

QT_END_NAMESPACE

#endif // SERVERCFGR25647_H
